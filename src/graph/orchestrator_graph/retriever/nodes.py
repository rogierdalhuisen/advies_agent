"""Node factory functions for the structured retriever pipeline."""

import logging
from typing import Literal

from pydantic import BaseModel, Field

from src.retrieval.retriever import InsuranceRetriever
from src.retrieval.reranker.reranker import Reranker
from ..schemas import RetrievalSummary
from .state import RetrieverState
from .prompts import GRADING_PROMPT, REWRITE_PROMPT, SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)


class GradeResult(BaseModel):
    """3-way classification of document relevance."""

    status: Literal["direct", "indirect", "miss"] = Field(
        description=(
            "direct: docs answer the query directly. "
            "indirect: docs explain why something is excluded or answer indirectly. "
            "miss: docs do not answer the query at all."
        )
    )


def make_retrieve(retriever: InsuranceRetriever, k: int = 30):
    """Create a retrieve node that searches the vector store filtered by provider."""

    def retrieve(state: RetrieverState) -> dict:
        query = state.get("current_query") or state["query"]
        provider = state["provider"]
        results = retriever.retrieve_company_docs(query, provider, k=k)
        docs = [doc for doc, _score in results] if results else []
        return {"documents": docs, "current_query": query}

    return retrieve


def make_rerank(reranker: Reranker, top_n: int = 8):
    """Create a rerank node that reranks retrieved documents."""

    def rerank(state: RetrieverState) -> dict:
        query = state.get("current_query") or state["query"]
        reranked = reranker.rerank(query, state.get("documents", []), top_n=top_n)
        return {"documents": reranked}

    return rerank


def make_grade(retriever: InsuranceRetriever, llm):
    """Create a grade node that classifies document relevance (direct/indirect/miss)."""

    def grade(state: RetrieverState) -> dict:
        query = state.get("current_query") or state["query"]
        docs = state.get("documents", [])
        docs_text = "\n---\n".join(
            retriever.format_document_with_context(doc) for doc in docs
        )
        prompt = GRADING_PROMPT.format(query=query, docs_text=docs_text)
        result = llm.with_structured_output(GradeResult).invoke(prompt)
        return {"evaluation_status": result.status}

    return grade


def make_rewrite(llm):
    """Create a rewrite node that rewrites the query on a miss."""

    def rewrite(state: RetrieverState) -> dict:
        original_query = state["query"]
        current_query = state.get("current_query") or original_query
        prompt = REWRITE_PROMPT.format(
            original_query=original_query,
            current_query=current_query,
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

        prompt = SUMMARIZE_PROMPT.format(
            aspect=aspect,
            provider=provider,
            product_description=product_description,
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
