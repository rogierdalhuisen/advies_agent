"""Self-reflective RAG graph with retrieval, reranking, grading, and query rewriting."""

from langgraph.graph import StateGraph, START, END

from .state import RetrieverState
from .nodes import retrieve, rerank, grade, rewrite, generate


def route_after_grading(state: RetrieverState) -> str:
    """Route based on grading result: generate or rewrite."""
    if state.evaluation_status in ("direct", "indirect"):
        return "generate"
    if state.retries >= state.max_retries:
        return "generate"
    return "rewrite"


# Build graph
workflow = StateGraph(RetrieverState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("rerank", rerank)
workflow.add_node("grade", grade)
workflow.add_node("rewrite", rewrite)
workflow.add_node("generate", generate)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "rerank")
workflow.add_edge("rerank", "grade")
workflow.add_conditional_edges("grade", route_after_grading, {"generate": "generate", "rewrite": "rewrite"})
workflow.add_edge("rewrite", "retrieve")
workflow.add_edge("generate", END)

graph = workflow.compile()
