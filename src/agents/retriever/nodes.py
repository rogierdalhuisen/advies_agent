"""Node functions for the self-reflective RAG retriever graph."""

from typing import Literal
from pydantic import BaseModel, Field

from .state import RetrieverState
from .config import retriever, reranker, grading_llm, rewrite_llm, generation_llm


class GradeResult(BaseModel):
    """3-way classification of document relevance."""

    status: Literal["direct", "indirect", "miss"] = Field(
        description=(
            "direct: docs answer the query directly. "
            "indirect: docs explain why something is excluded or answer indirectly. "
            "miss: docs do not answer the query at all."
        )
    )


def retrieve(state: RetrieverState) -> dict:
    """Retrieve documents filtered by insurance provider."""
    query = state.current_query or state.original_query
    results = retriever.retrieve_company_docs(query, state.insurance_provider, k=10)
    return {"documents": [doc for doc, _ in results], "current_query": query}


def rerank(state: RetrieverState) -> dict:
    """Rerank retrieved documents."""
    return {"documents": reranker.rerank(state.current_query, state.documents, top_n=5)}


def grade(state: RetrieverState) -> dict:
    """Grade document relevance with a 3-way LLM classification."""
    docs_text = "\n---\n".join(
        retriever.format_document_with_context(doc) for doc in state.documents
    )
    result = grading_llm.with_structured_output(GradeResult).invoke(
        f"Query: {state.current_query}\n\n"
        f"Documents:\n{docs_text}\n\n"
        "Classify whether these documents answer the query directly, "
        "indirectly (e.g. explaining why something is excluded), "
        "or not at all (miss)."
    )
    return {"evaluation_status": result.status}


def rewrite(state: RetrieverState) -> dict:
    """Rewrite the query for a better retrieval attempt."""
    msg = rewrite_llm.invoke(
        f"The following query did not yield relevant results:\n"
        f"Original query: {state.original_query}\n"
        f"Last query tried: {state.current_query}\n\n"
        f"Rewrite the query to improve retrieval. "
        f"Return only the rewritten query, nothing else."
    )
    return {"current_query": msg.content.strip(), "retries": state.retries + 1}


def generate(state: RetrieverState) -> dict:
    """Generate a final answer from the retrieved documents."""
    docs_text = "\n---\n".join(
        retriever.format_document_with_context(doc) for doc in state.documents
    )
    prompt = f"Query: {state.original_query}\n\nDocuments:\n{docs_text}\n\n"

    if state.evaluation_status == "direct":
        prompt += "Answer the query based on the documents above."
    else:
        prompt += (
            "The documents don't answer the query directly but contain "
            "relevant indirect information. Summarize what the documents "
            "say that relates to the query."
        )

    return {"answer": generation_llm.invoke(prompt).content}
