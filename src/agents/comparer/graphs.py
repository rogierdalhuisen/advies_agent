"""Comparer agent: runs retrieval for multiple providers in parallel, then compares."""

from langgraph.graph import StateGraph, START, END
from .state import RetrieverState, ComparerState
from .config import retriever, reranker, grading_llm, rewrite_llm, generation_llm
from .nodes import (
    make_retrieve, make_rerank, make_grade, make_rewrite, make_generate,
    make_retrieve_all, make_compare,
)


def _build_retriever_subgraph():
    """Build the single-provider retriever subgraph (retrieve → rerank → grade → rewrite loop → generate)."""
    workflow = StateGraph(RetrieverState)

    workflow.add_node("retrieve", make_retrieve(retriever))
    workflow.add_node("rerank", make_rerank(reranker))
    workflow.add_node("grade", make_grade(retriever, grading_llm))
    workflow.add_node("rewrite", make_rewrite(rewrite_llm))
    workflow.add_node("generate", make_generate(retriever, generation_llm))

    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "rerank")
    workflow.add_edge("rerank", "grade")
    workflow.add_conditional_edges(
        "grade",
        _route_after_grading,
        {"generate": "generate", "rewrite": "rewrite"},
    )
    workflow.add_edge("rewrite", "retrieve")
    workflow.add_edge("generate", END)

    return workflow.compile()


def _route_after_grading(state: RetrieverState) -> str:
    if state.evaluation_status in ("direct", "indirect"):
        return "generate"
    if state.retries >= state.max_retries:
        return "generate"
    return "rewrite"


class ComparerAgent:
    """Runs retrieval for 2-3 insurance providers in parallel, then compares results."""

    def __init__(self):
        self.retriever_subgraph = _build_retriever_subgraph()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ComparerState)

        workflow.add_node("retrieve_all", make_retrieve_all(self.retriever_subgraph))
        workflow.add_node("compare", make_compare(generation_llm))

        workflow.add_edge(START, "retrieve_all")
        workflow.add_edge("retrieve_all", "compare")
        workflow.add_edge("compare", END)

        return workflow.compile()

    def invoke(self, query: str, insurance_providers: list[str]) -> dict:
        """Run the comparer graph.

        Args:
            query: The insurance question to answer.
            insurance_providers: List of 2-3 provider names to compare.
        """
        return self.graph.invoke({
            "original_query": query,
            "insurance_providers": insurance_providers,
        })
