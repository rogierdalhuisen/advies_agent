"""Node functions for the orchestrator agent."""

import json

from langchain_core.messages import SystemMessage, HumanMessage

from ..config import opus_llm
from ..state import OrchestratorState
from ..schemas import AssessmentResult
from .prompts import ORCHESTRATOR_ASSESS_PROMPT


def build_initial_tracker_node(state: OrchestratorState) -> dict:
    """Build the retrieval tracker skeleton from providers and aspects. Pure Python, no LLM."""
    parsed = state["parsed_constraints"]
    premiums = state["premiums"]
    providers = state["available_providers"]
    aspects = parsed.get("retrieval_aspects", [])
    if not isinstance(aspects, list):
        aspects = []

    tracker = {}
    for provider in providers:
        # Build aspect tracking
        aspect_tracker = {}
        for aspect_info in aspects:
            aspect_name = aspect_info["aspect"] if isinstance(aspect_info, dict) else aspect_info.aspect
            aspect_tracker[aspect_name] = {
                "status": "pending",
                "summaries": [],
            }

        # Build coverage level tracking from premiums
        coverage_levels = {}
        provider_premiums = premiums.get(provider, {})
        for level in provider_premiums:
            coverage_levels[level] = {"status": "active"}

        tracker[provider] = {
            "status": "active",
            "aspects": aspect_tracker,
            "coverage_levels": coverage_levels,
        }

    return {
        "retrieval_tracker": tracker,
        "retrieval_iteration": 0,
        "retrieval_tasks": [],
        "orchestrator_notes": [],
    }


def orchestrator_assess_node(state: OrchestratorState) -> dict:
    """Assess current retrieval state and decide next steps using Opus."""
    llm = opus_llm.with_structured_output(AssessmentResult)

    context = {
        "parsed_constraints": state["parsed_constraints"],
        "product_descriptions": state["product_descriptions"],
        "premiums": state["premiums"],
        "retrieval_tracker": state["retrieval_tracker"],
        "retrieval_iteration": state["retrieval_iteration"],
        "orchestrator_notes": state.get("orchestrator_notes", []),
    }

    response = llm.invoke([
        SystemMessage(content=ORCHESTRATOR_ASSESS_PROMPT),
        HumanMessage(content=json.dumps(context, ensure_ascii=False, default=str)),
    ])

    # Update retrieval tracker with provider status changes
    tracker = state["retrieval_tracker"].copy()
    for update in response.provider_updates:
        if update.provider in tracker:
            tracker[update.provider]["status"] = update.status

    # Update coverage level statuses
    for cl_update in response.coverage_level_updates:
        provider = cl_update.provider
        level = cl_update.coverage_level
        if provider in tracker and level in tracker[provider].get("coverage_levels", {}):
            tracker[provider]["coverage_levels"][level]["status"] = cl_update.status

    # Append notes
    notes = list(state.get("orchestrator_notes", []))
    notes.append(f"Iteratie {state['retrieval_iteration']}: {response.notes}")

    return {
        "retrieval_tracker": tracker,
        "retrieval_tasks": [task.model_dump() for task in response.retrieval_tasks],
        "orchestrator_notes": notes,
    }


def route_after_assessment(state: OrchestratorState) -> str:
    """Conditional edge: dispatch retrievers or proceed to evaluation."""
    tasks = state.get("retrieval_tasks", [])
    iteration = state.get("retrieval_iteration", 0)

    if tasks and iteration < 2:
        return "retrieve"
    return "evaluate"
