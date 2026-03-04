"""Node factory functions for the structured retriever pipeline."""

import logging
from typing import Literal

from pydantic import BaseModel, Field

from src.retrieval.retriever import InsuranceRetriever
from src.retrieval.reranker.reranker import Reranker
from ..schemas import RetrievalSummary
from .state import RetrieverState
from .prompts import VERIFY_PROMPT, REWRITE_PROMPT, SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)

# Keywords that trigger pregnancy-related retrieval boost
PREGNANCY_KEYWORDS: set[str] = {
    "pregnancy", "maternity", "zwangerschap", "bevalling", "prenatal", "zwanger",
}


class VerifyResult(BaseModel):
    """3-way verification of document relevance with missing-info tracking."""

    status: Literal["complete", "partial", "miss"] = Field(
        description=(
            "complete: docs fully answer the query. "
            "partial: docs answer part of the query but information is missing. "
            "miss: docs do not answer the query at all."
        )
    )
    missing_info: str = Field(
        default="",
        description="What information is still missing (populated when status='partial').",
    )


def _has_pregnancy_keywords(text: str) -> bool:
    """Check if text contains any pregnancy-related keywords (case-insensitive)."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in PREGNANCY_KEYWORDS)


def make_retrieve(retriever: InsuranceRetriever, k: int = 30):
    """Create a retrieve node with pregnancy keyword boost and retained-doc merging."""

    def retrieve(state: RetrieverState) -> dict:
        query = state.get("current_query") or state["query"]
        provider = state["provider"]

        # Pregnancy boost: increase k for broader recall
        effective_k = 50 if _has_pregnancy_keywords(query) else k

        results = retriever.retrieve_company_docs(query, provider, k=effective_k)
        new_docs = [doc for doc, _score in results] if results else []

        # Merge with retained documents from previous loops
        retained = state.get("retained_documents", [])
        merged = retained + new_docs

        return {"documents": merged, "current_query": query}

    return retrieve


def make_rerank(reranker: Reranker, top_n: int = 8, rewrite_top_n: int = 12):
    """Create a rerank node with dynamic top_n based on retries and pregnancy boost."""

    def rerank(state: RetrieverState) -> dict:
        query = state.get("current_query") or state["query"]

        # Determine effective top_n
        if _has_pregnancy_keywords(query):
            effective_top_n = 15
        elif state.get("retries", 0) > 0:
            effective_top_n = rewrite_top_n
        else:
            effective_top_n = top_n

        reranked = reranker.rerank(query, state.get("documents", []), top_n=effective_top_n)
        return {"documents": reranked}

    return rerank


def make_verify(retriever: InsuranceRetriever, llm):
    """Create a verify node that classifies document relevance (complete/partial/miss)."""

    def verify(state: RetrieverState) -> dict:
        query = state.get("current_query") or state["query"]
        docs = state.get("documents", [])
        docs_text = "\n---\n".join(
            retriever.format_document_with_context(doc) for doc in docs
        )
        prompt = VERIFY_PROMPT.format(query=query, docs_text=docs_text)
        result = llm.with_structured_output(VerifyResult).invoke(prompt)
        return {"evaluation_status": result.status, "missing_info": result.missing_info}

    return verify


def save_documents(state: RetrieverState) -> dict:
    """Save current documents to retained_documents before a rewrite loop."""
    return {"retained_documents": state.get("documents", [])}


def make_rewrite(llm):
    """Create a rewrite node that uses missing_info to target gaps."""

    def rewrite(state: RetrieverState) -> dict:
        original_query = state["query"]
        current_query = state.get("current_query") or original_query
        missing_info = state.get("missing_info", "")
        prompt = REWRITE_PROMPT.format(
            original_query=original_query,
            current_query=current_query,
            missing_info=missing_info,
        )
        msg = llm.invoke(prompt)
        retries = state.get("retries", 0)
        return {"current_query": msg.content.strip(), "retries": retries + 1}

    return rewrite


def make_summarize(retriever: InsuranceRetriever, llm):
    """Create a summarize node that produces a RetrievalSummary via structured output."""

    def summarize(state: RetrieverState) -> dict:
        docs = state.get("documents", [])
        docs_text = "\n---\n".join(
            retriever.format_document_with_context(doc) for doc in docs
        ) if docs else "Geen documenten gevonden."

        provider = state["provider"]
        aspect = state["aspect"]
        product_description = state.get("product_description", "Geen beschrijving beschikbaar.")
        evaluation_status = state.get("evaluation_status", "complete")

        prompt = SUMMARIZE_PROMPT.format(
            aspect=aspect,
            provider=provider,
            product_description=product_description,
            evaluation_status=evaluation_status,
            docs_text=docs_text,
        )

        try:
            summary = llm.with_structured_output(RetrievalSummary).invoke(prompt)
            # Ensure provider and aspect match state (LLM might hallucinate different values)
            summary.provider = provider
            summary.aspect = aspect
            return {"retrieval_summary": summary.model_dump()}
        except Exception as e:
            logger.warning("Failed to produce structured summary: %s", e)
            fallback = RetrievalSummary(
                provider=provider,
                aspect=aspect,
                overall_summary="Samenvatting kon niet worden gegenereerd.",
                coverage_level_findings=[],
                information_not_found="Structured output parsing mislukt.",
                confidence="low",
                ambiguities=str(e),
            )
            return {"retrieval_summary": fallback.model_dump()}

    return summarize
