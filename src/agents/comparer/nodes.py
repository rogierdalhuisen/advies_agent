"""Node functions for the comparer agent."""

from typing import Literal
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel, Field

from src.retrieval.retriever import InsuranceRetriever
from src.retrieval.reranker.reranker import Reranker
from .state import RetrieverState, ComparerState, ProviderResult


class GradeResult(BaseModel):
    """3-way classification of document relevance."""

    status: Literal["direct", "indirect", "miss"] = Field(
        description=(
            "direct: docs answer the query directly. "
            "indirect: docs explain why something is excluded or answer indirectly. "
            "miss: docs do not answer the query at all."
        )
    )


# --- Single-provider retriever nodes (used inside the subgraph) ---


def make_retrieve(retriever: InsuranceRetriever):
    def retrieve(state: RetrieverState) -> dict:
        query = state.current_query or state.original_query
        results = retriever.retrieve_company_docs(query, state.insurance_provider, k=state.k)
        return {"documents": [doc for doc, _ in results], "current_query": query}
    return retrieve


def make_rerank(reranker: Reranker):
    def rerank(state: RetrieverState) -> dict:
        return {"documents": reranker.rerank(state.current_query, state.documents, top_n=state.top_n)}
    return rerank


def make_grade(retriever: InsuranceRetriever, llm):
    def grade(state: RetrieverState) -> dict:
        docs_text = "\n---\n".join(
            retriever.format_document_with_context(doc) for doc in state.documents
        )
        result = llm.with_structured_output(GradeResult).invoke(
            f"Query: {state.current_query}\n\n"
            f"Documents:\n{docs_text}\n\n"
            "Classify whether these documents answer the query directly, "
            "indirectly (e.g. explaining why something is excluded), "
            "or not at all (miss)."
        )
        return {"evaluation_status": result.status}
    return grade


def make_rewrite(llm):
    def rewrite(state: RetrieverState) -> dict:
        msg = llm.invoke(
            f"The following query did not yield relevant results:\n"
            f"Original query: {state.original_query}\n"
            f"Last query tried: {state.current_query}\n\n"
            f"Rewrite the query to improve retrieval. "
            f"Return only the rewritten query, nothing else."
        )
        return {"current_query": msg.content.strip(), "retries": state.retries + 1}
    return rewrite


def make_generate(retriever: InsuranceRetriever, llm):
    def generate(state: RetrieverState) -> dict:
        docs_text = "\n---\n".join(
            retriever.format_document_with_context(doc) for doc in state.documents
        )
        prompt = f"Query: {state.original_query}\n\nDocuments:\n{docs_text}\n\n"

        if state.evaluation_status == "direct":
            prompt += "Answer the query based on the documents above. Give a concise and accurate answer with respect to the query"
        else:
            prompt += (
                "The documents don't answer the query directly but contain "
                "relevant indirect information. Summarize what the documents "
                "say that relates to the query."
            )

        response = llm.invoke(prompt)
        text = response.content
        if isinstance(text, list):
            text = "".join(block["text"] for block in text if block.get("type") == "text")
        return {"answer": text}
    return generate


# --- Outer comparer nodes ---


def make_retrieve_all(retriever_subgraph):
    """Run the retriever subgraph for each provider in parallel."""

    def retrieve_all(state: ComparerState) -> dict:
        def run_for_provider(provider: str) -> ProviderResult:
            result = retriever_subgraph.invoke({
                "original_query": state.original_query,
                "insurance_provider": provider,
                "k": state.k,
                "top_n": state.top_n,
            })
            return ProviderResult(
                insurance_provider=provider,
                answer=result["answer"],
            )

        with ThreadPoolExecutor(max_workers=len(state.insurance_providers)) as pool:
            results = list(pool.map(run_for_provider, state.insurance_providers))

        return {"provider_results": results}

    return retrieve_all


def make_compare(llm):
    """Compare and summarize results across providers."""

    def compare(state: ComparerState) -> dict:
        results_text = "\n\n".join(
            f"### {r.insurance_provider}\n{r.answer}"
            for r in state.provider_results
        )
        providers = ", ".join(r.insurance_provider for r in state.provider_results)

        response = llm.invoke(
            f"Query: {state.original_query}\n\n"
            f"Below are the answers for each insurance provider ({providers}):\n\n"
            f"{results_text}\n\n"
            "Compare and summarize the differences and similarities between "
            "these insurance providers with respect to the query. "
            "Highlight key differences, advantages, and disadvantages of each."
        )
        text = response.content
        if isinstance(text, list):
            text = "".join(block["text"] for block in text if block.get("type") == "text")
        return {"comparison": text}

    return compare
