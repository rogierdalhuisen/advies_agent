"""State definitions for the hierarchical orchestrator."""

import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


class OrchestratorState(TypedDict):
    """Main graph state for the hierarchical orchestrator."""
    messages: Annotated[list[AnyMessage], add_messages]

    # Input (set once at start)
    user_profile: dict
    premiums: dict  # provider -> coverage_level -> {total, deductible, per_person}
    product_descriptions: dict  # provider -> static markdown
    available_providers: list[str]

    # User Agent output
    parsed_constraints: dict  # ParsedConstraints schema

    # Retrieval tracking
    retrieval_tracker: dict  # provider -> {status, aspects -> {status, summaries[]}, coverage_levels -> {status}}

    # Collects retrieval summaries from parallel Send() invocations via operator.add reducer
    retrieval_summaries: Annotated[list[dict], operator.add]

    # Orchestrator control
    retrieval_tasks: list[dict]  # [{provider, query, aspect}]
    retrieval_iteration: int  # max 4
    orchestrator_notes: list[str]  # decision log

    # Evaluator outputs
    qualitative_assessment: dict  # QualitativeAssessment schema
    recommendation: dict  # FinalRecommendation schema


class RetrieverSubState(TypedDict):
    """Subgraph state for each retriever invocation."""
    messages: Annotated[list[AnyMessage], add_messages]
    provider: str
    query: str
    aspect: str
    product_description: str
    retrieval_summary: dict  # Set when submit_summary is called
