"""Structured retriever pipeline subgraph for the hierarchical orchestrator."""

from langgraph.graph import StateGraph, START, END

from ..config import insurance_retriever, reranker, summary_llm, grading_llm, rewrite_llm
from .state import RetrieverState
from .nodes import make_retrieve, make_rerank, make_grade, make_rewrite, make_summarize


class RetrieverAgent:
    """Deterministic retrieve → rerank → grade → [rewrite loop] → summarize pipeline."""

    def __init__(self, k: int = 30, top_n: int = 8, max_retries: int = 3):
        self.max_retries = max_retries
        self.graph = self._build_graph(k=k, top_n=top_n)

    def _build_graph(self, k: int, top_n: int):
        workflow = StateGraph(RetrieverState)

        workflow.add_node("retrieve", make_retrieve(insurance_retriever, k=k))
        workflow.add_node("rerank", make_rerank(reranker, top_n=top_n))
        workflow.add_node("grade", make_grade(insurance_retriever, grading_llm))
        workflow.add_node("rewrite", make_rewrite(rewrite_llm))
        workflow.add_node("summarize", make_summarize(insurance_retriever, summary_llm))

        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "rerank")
        workflow.add_edge("rerank", "grade")
        workflow.add_conditional_edges(
            "grade",
            self._route_after_grading,
            {"summarize": "summarize", "rewrite": "rewrite"},
        )
        workflow.add_edge("rewrite", "retrieve")
        workflow.add_edge("summarize", END)

        return workflow.compile()

    def _route_after_grading(self, state: RetrieverState) -> str:
        if state.get("evaluation_status") in ("direct", "indirect"):
            return "summarize"
        if state.get("retries", 0) >= self.max_retries:
            return "summarize"
        return "rewrite"

    def invoke(self, input_state: dict, **kwargs) -> dict:
        return self.graph.invoke(input_state, **kwargs)


def build_retriever_subgraph(k: int = 30, top_n: int = 8, max_retries: int = 1):
    """Build and return the compiled retriever subgraph."""
    subgraph = RetrieverAgent(k=k, top_n=top_n, max_retries=max_retries)
    return subgraph.graph


retriever_agent = build_retriever_subgraph()
