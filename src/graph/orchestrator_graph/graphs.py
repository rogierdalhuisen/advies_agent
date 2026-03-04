"""Main hierarchical orchestrator graph with Send() pattern for parallel retrieval."""

import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from .state import OrchestratorState
from .config import load_product_descriptions
from .user_agent import user_agent_node
from .orchestrator import (
    build_initial_tracker_node,
    orchestrator_assess_node,
    route_after_assessment,
)
from .retriever_agent import retriever_agent
from .tradeoff_agent import evaluator_step1_node, evaluator_step2_node


def _run_retriever(state: dict) -> dict:
    """Wrapper that invokes the retriever subgraph and returns summary for the parent state.

    Receives input from Send() with provider, query, aspect, product_description.
    Returns a single retrieval_summary wrapped in a list for the operator.add reducer.
    """
    result = retriever_agent.invoke({
        "messages": [HumanMessage(content=state["query"])],
        "provider": state["provider"],
        "query": state["query"],
        "aspect": state["aspect"],
        "product_description": state.get("product_description", ""),
        "retrieval_summary": {},
    })

    summary = result.get("retrieval_summary", {})
    return {"retrieval_summaries": [summary]}


def _fan_out_retrievers(state: OrchestratorState) -> list[Send]:
    """Create a Send() for each retrieval task, dispatching to parallel retriever executions."""
    tasks = state.get("retrieval_tasks", [])
    product_descriptions = state.get("product_descriptions", {})

    sends = []
    for task in tasks:
        provider = task["provider"]
        sends.append(
            Send(
                "retriever",
                {
                    "provider": provider,
                    "query": task["query"],
                    "aspect": task["aspect"],
                    "product_description": product_descriptions.get(provider, ""),
                },
            )
        )
    return sends


def _dispatch_or_evaluate(state: OrchestratorState) -> list[Send] | str:
    """Conditional edge: fan out to retrievers or proceed to evaluation."""
    direction = route_after_assessment(state)
    if direction == "retrieve":
        return _fan_out_retrievers(state)
    return "evaluator_step1"


def _merge_retriever_results(state: OrchestratorState) -> dict:
    """Merge accumulated retrieval summaries into the tracker.

    After Send() completes, all retriever outputs are collected in
    state['retrieval_summaries'] via the operator.add reducer.
    This node processes them into the structured retrieval_tracker.
    """
    # Deep copy the tracker
    tracker = {}
    for provider, pdata in state["retrieval_tracker"].items():
        tracker[provider] = {
            "status": pdata["status"],
            "aspects": {},
            "coverage_levels": {k: {**v} for k, v in pdata.get("coverage_levels", {}).items()},
        }
        for aspect_name, adata in pdata["aspects"].items():
            tracker[provider]["aspects"][aspect_name] = {
                "status": adata["status"],
                "summaries": list(adata["summaries"]),
            }

    # Process all accumulated summaries from the parallel retrievers
    # In _merge_retriever_results, replace the append block:
    for summary in state.get("retrieval_summaries", []):
        if not summary or not summary.get("provider"):
            continue
        provider = summary["provider"]
        aspect = summary["aspect"]
        if provider in tracker and aspect in tracker[provider]["aspects"]:
            # Only add if this aspect doesn't already have a summary
            if not tracker[provider]["aspects"][aspect]["summaries"]:
                tracker[provider]["aspects"][aspect]["summaries"].append(summary)
            tracker[provider]["aspects"][aspect]["status"] = "retrieved"

    return {
        "retrieval_tracker": tracker,
        "retrieval_iteration": state.get("retrieval_iteration", 0) + 1,
        "retrieval_summaries": [],  # Clear after processing
    }


class HierarchicalAgent:
    """Hierarchical orchestrator for insurance recommendation.

    Architecture: user_agent -> build_tracker -> orchestrator_assess -> [retrievers] -> merge
    -> orchestrator_assess (loop) -> evaluator_step1 -> evaluator_step2 -> END
    """

    def __init__(self):
        self.product_descriptions = load_product_descriptions()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the hierarchical orchestrator StateGraph."""
        workflow = StateGraph(OrchestratorState)

        # Add nodes
        workflow.add_node("user_agent", user_agent_node)
        workflow.add_node("build_tracker", build_initial_tracker_node)
        workflow.add_node("orchestrator_assess", orchestrator_assess_node)
        workflow.add_node("retriever", _run_retriever)
        workflow.add_node("merge_results", _merge_retriever_results)
        workflow.add_node("evaluator_step1", evaluator_step1_node)
        workflow.add_node("evaluator_step2", evaluator_step2_node)

        # Linear start: parse user profile then build tracker
        workflow.add_edge(START, "user_agent")
        workflow.add_edge("user_agent", "build_tracker")
        workflow.add_edge("build_tracker", "orchestrator_assess")

        # Conditional: fan out to retrievers (Send) or proceed to evaluator_step1
        workflow.add_conditional_edges(
            "orchestrator_assess",
            _dispatch_or_evaluate,
            ["retriever", "evaluator_step1"],
        )

        # After retrieval, merge results and loop back to orchestrator
        workflow.add_edge("retriever", "merge_results")
        workflow.add_edge("merge_results", "orchestrator_assess")

        # Evaluation chain
        workflow.add_edge("evaluator_step1", "evaluator_step2")
        workflow.add_edge("evaluator_step2", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _build_initial_state(
        self,
        user_profile: dict,
        premiums: dict,
        available_providers: list[str],
        product_descriptions: dict | None = None,
    ) -> dict:
        """Build the initial state dict for graph execution."""
        descriptions = product_descriptions or self.product_descriptions
        return {
            "messages": [],
            "user_profile": user_profile,
            "premiums": premiums,
            "product_descriptions": descriptions,
            "available_providers": available_providers,
            "parsed_constraints": {},
            "retrieval_tracker": {},
            "retrieval_summaries": [],
            "retrieval_tasks": [],
            "retrieval_iteration": 0,
            "orchestrator_notes": [],
            "qualitative_assessment": {},
            "recommendation": {},
        }

    def _make_config(self, thread_id: str | None = None) -> dict:
        """Build a LangGraph config with a thread_id for checkpointing."""
        return {"configurable": {"thread_id": thread_id or uuid.uuid4().hex}}

    def invoke(
        self,
        user_profile: dict,
        premiums: dict,
        available_providers: list[str],
        product_descriptions: dict | None = None,
        thread_id: str | None = None,
    ) -> dict:
        """Run the hierarchical orchestrator end-to-end.

        Args:
            user_profile: Client profile data from the advice form.
            premiums: Premiums keyed by provider -> coverage_level -> amounts.
            available_providers: List of provider names to consider.
            product_descriptions: Static product descriptions per provider.
                                  If None, uses auto-loaded descriptions.
            thread_id: Optional thread ID for checkpointing. If None, a random
                       ID is generated. Re-use the same ID to resume a failed run.

        Returns:
            Final state dict with 'recommendation' containing FinalRecommendation.
        """
        initial_state = self._build_initial_state(
            user_profile, premiums, available_providers, product_descriptions
        )
        return self.graph.invoke(initial_state, config=self._make_config(thread_id))

    def stream(
        self,
        user_profile: dict,
        premiums: dict,
        available_providers: list[str],
        product_descriptions: dict | None = None,
        stream_mode: str = "updates",
        thread_id: str | None = None,
    ):
        """Stream orchestrator execution, yielding state updates per node.

        Args:
            user_profile: Client profile data from the advice form.
            premiums: Premiums keyed by provider -> coverage_level -> amounts.
            available_providers: List of provider names to consider.
            product_descriptions: Static product descriptions per provider.
            stream_mode: "updates" (delta per node), "values" (full state per node),
                         or "debug" (detailed checkpoint info).
            thread_id: Optional thread ID for checkpointing. If None, a random
                       ID is generated. Re-use the same ID to resume a failed run.

        Yields:
            State updates per completed node (format depends on stream_mode).
        """
        initial_state = self._build_initial_state(
            user_profile, premiums, available_providers, product_descriptions
        )
        yield from self.graph.stream(
            initial_state, config=self._make_config(thread_id), stream_mode=stream_mode
        )
