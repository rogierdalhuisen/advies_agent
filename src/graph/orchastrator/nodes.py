"""Node functions for the hierarchical orchestrator graph."""

import json

from langchain_core.messages import SystemMessage, HumanMessage

from .config import opus_llm, retriever_llm
from .state import OrchestratorState
from .schemas import (
    ParsedConstraints,
    AssessmentResult,
    QualitativeAssessment,
    FinalRecommendation,
)
from .prompts import (
    USER_AGENT_PROMPT,
    ORCHESTRATOR_ASSESS_PROMPT,
    EVALUATOR_STEP1_PROMPT,
    EVALUATOR_STEP2_PROMPT,
)


def user_agent_node(state: OrchestratorState) -> dict:
    """Parse user profile into structured constraints using Opus."""
    llm = retriever_llm.with_structured_output(ParsedConstraints)

    response = llm.invoke([
        SystemMessage(content=USER_AGENT_PROMPT),
        HumanMessage(content=json.dumps(state["user_profile"], ensure_ascii=False, default=str)),
    ])

    return {"parsed_constraints": response.model_dump()}


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


def evaluator_step1_node(state: OrchestratorState) -> dict:
    """Produce qualitative assessment of all active provider-coverage combinations."""
    llm = retriever_llm.with_structured_output(QualitativeAssessment)

    context = {
        "parsed_constraints": state["parsed_constraints"],
        "retrieval_tracker": state["retrieval_tracker"],
        "premiums": state["premiums"],
        "product_descriptions": state["product_descriptions"],
    }

    response = llm.invoke([
        SystemMessage(content=EVALUATOR_STEP1_PROMPT),
        HumanMessage(content=json.dumps(context, ensure_ascii=False, default=str)),
    ])

    return {"qualitative_assessment": response.model_dump()}


def evaluator_step2_node(state: OrchestratorState) -> dict:
    """Produce final recommendation from qualitative assessment."""
    llm = opus_llm.with_structured_output(FinalRecommendation)

    context = {
        "parsed_constraints": state["parsed_constraints"],
        "retrieval_tracker": state["retrieval_tracker"],
        "premiums": state["premiums"],
        "product_descriptions": state["product_descriptions"],
        "qualitative_assessment": state["qualitative_assessment"],
    }

    response = llm.invoke([
        SystemMessage(content=EVALUATOR_STEP2_PROMPT),
        HumanMessage(content=json.dumps(context, ensure_ascii=False, default=str)),
    ])

    return {"recommendation": response.model_dump()}
