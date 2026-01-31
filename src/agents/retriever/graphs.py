"""Self-reflective RAG agent with retrieval, reranking, grading, and query rewriting."""

from langgraph.graph import StateGraph, START, END
from .state import RetrieverState
from .config import retriever, reranker, grading_llm, rewrite_llm, generation_llm
from .nodes import make_retrieve, make_rerank, make_grade, make_rewrite, make_generate


class RetrieverAgent:
    """Self-reflective RAG agent. All configuration comes from config.py."""

    def __init__(self):
        self.retriever = retriever
        self.reranker = reranker
        self.grading_llm = grading_llm
        self.rewrite_llm = rewrite_llm
        self.generation_llm = generation_llm
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(RetrieverState)

        workflow.add_node("retrieve", make_retrieve(self.retriever))
        workflow.add_node("rerank", make_rerank(self.reranker))
        workflow.add_node("grade", make_grade(self.retriever, self.grading_llm))
        workflow.add_node("rewrite", make_rewrite(self.rewrite_llm))
        workflow.add_node("generate", make_generate(self.retriever, self.generation_llm))

        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "rerank")
        workflow.add_edge("rerank", "grade")
        workflow.add_conditional_edges(
            "grade",
            self._route_after_grading,
            {"generate": "generate", "rewrite": "rewrite"},
        )
        workflow.add_edge("rewrite", "retrieve")
        workflow.add_edge("generate", END)

        return workflow.compile()

    @staticmethod
    def _route_after_grading(state: RetrieverState) -> str:
        if state.evaluation_status in ("direct", "indirect"):
            return "generate"
        if state.retries >= state.max_retries:
            return "generate"
        return "rewrite"

    def invoke(self, query: str, insurance_provider: str) -> dict:
        """Convenience method to run the graph."""
        return self.graph.invoke({
            "original_query": query,
            "insurance_provider": insurance_provider,
        })
