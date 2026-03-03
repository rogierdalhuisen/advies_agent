"""Node functions for the tradeoff (evaluator) agent."""

import json

from langchain_core.messages import SystemMessage, HumanMessage

from ..config import tradeoff_llm
from ..state import OrchestratorState
from ..schemas import QualitativeAssessment, FinalRecommendation
from .prompts import EVALUATOR_STEP1_PROMPT, EVALUATOR_STEP2_PROMPT


def _filter_active_tracker(tracker: dict) -> dict:
    """Return tracker with only active providers and active coverage levels."""
    filtered = {}
    for provider, pdata in tracker.items():
        if pdata.get("status") != "active":
            continue
        active_levels = {
            k: v for k, v in pdata.get("coverage_levels", {}).items()
            if v.get("status") == "active"
        }
        if active_levels:
            filtered[provider] = {**pdata, "coverage_levels": active_levels}
    return filtered


def evaluator_step1_node(state: OrchestratorState) -> dict:
    """Produce qualitative assessment of all active provider-coverage combinations."""
    llm = tradeoff_llm.with_structured_output(QualitativeAssessment)

    filtered_tracker = _filter_active_tracker(state["retrieval_tracker"])

    context = {
        "parsed_constraints": state["parsed_constraints"],
        "retrieval_tracker": filtered_tracker,
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
    llm = tradeoff_llm.with_structured_output(FinalRecommendation)

    filtered_tracker = _filter_active_tracker(state["retrieval_tracker"])

    context = {
        "parsed_constraints": state["parsed_constraints"],
        "retrieval_tracker": filtered_tracker,
        "premiums": state["premiums"],
        "product_descriptions": state["product_descriptions"],
        "qualitative_assessment": state["qualitative_assessment"],
    }

    response = llm.invoke([
        SystemMessage(content=EVALUATOR_STEP2_PROMPT),
        HumanMessage(content=json.dumps(context, ensure_ascii=False, default=str)),
    ])

    return {"recommendation": response.model_dump()}
