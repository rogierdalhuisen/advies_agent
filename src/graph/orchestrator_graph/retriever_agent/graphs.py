"""Structured retriever pipeline subgraph for the hierarchical orchestrator."""

from langgraph.graph import StateGraph, START, END

from ..config import insurance_retriever, reranker, summary_llm, verifier_llm, rewrite_llm
from .state import RetrieverState
from .nodes import (
    make_retrieve,
    make_rerank,
    make_verify,
    make_rewrite,
    make_summarize,
    save_documents,
)


class RetrieverAgent:
    """Retrieve → rerank → verify → [save → rewrite loop] → summarize pipeline."""

    def __init__(self, k: int = 30, top_n: int = 8, rewrite_top_n: int = 12, max_retries: int = 2):
        self.max_retries = max_retries
        self.graph = self._build_graph(k=k, top_n=top_n, rewrite_top_n=rewrite_top_n)

    def _build_graph(self, k: int, top_n: int, rewrite_top_n: int):
        workflow = StateGraph(RetrieverState)

        workflow.add_node("retrieve", make_retrieve(insurance_retriever, k=k))
        workflow.add_node("rerank", make_rerank(reranker, top_n=top_n, rewrite_top_n=rewrite_top_n))
        workflow.add_node("verify", make_verify(insurance_retriever, verifier_llm))
        workflow.add_node("save_documents", save_documents)
        workflow.add_node("rewrite", make_rewrite(rewrite_llm))
        workflow.add_node("summarize", make_summarize(insurance_retriever, summary_llm))

        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "rerank")
        workflow.add_edge("rerank", "verify")
        workflow.add_conditional_edges(
            "verify",
            self._route_after_verify,
            {"summarize": "summarize", "save_documents": "save_documents"},
        )
        workflow.add_edge("save_documents", "rewrite")
        workflow.add_edge("rewrite", "retrieve")
        workflow.add_edge("summarize", END)

        return workflow.compile()

    def _route_after_verify(self, state: RetrieverState) -> str:
        """Route based on verification result: complete/miss → summarize, partial → rewrite loop."""
        if state.get("evaluation_status") == "complete":
            return "summarize"
        if state.get("evaluation_status") == "miss":
            return "summarize"
        if state.get("retries", 0) >= self.max_retries:
            return "summarize"
        return "save_documents"

    def invoke(self, input_state: dict, **kwargs) -> dict:
        return self.graph.invoke(input_state, **kwargs)


def build_retriever_subgraph(k: int = 30, top_n: int = 8, rewrite_top_n: int = 12, max_retries: int = 2):
    """Build and return the compiled retriever subgraph."""
    subgraph = RetrieverAgent(k=k, top_n=top_n, rewrite_top_n=rewrite_top_n, max_retries=max_retries)
    return subgraph.graph


retriever_agent = build_retriever_subgraph()
