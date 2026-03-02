"""Pydantic output schemas for the hierarchical orchestrator."""

from typing import Literal
from pydantic import BaseModel, Field


# --- User Agent schemas ---

class RetrievalAspect(BaseModel):
    """A specific topic to investigate in policy documents."""
    aspect: str = Field(description="Topic to investigate (English)")
    description: str = Field(description="What to look for (Dutch)")
    priority: Literal["high", "medium", "low"]


class CoreConstraints(BaseModel):
    """Core client parameters for insurance recommendation."""
    age: int = Field(description="Client age")
    destination: str = Field(description="Travel destination")
    duration: str = Field(description="Trip or coverage duration")
    employment_type: str = Field(description="Type of employment")
    trip_type: str = Field(description="Type of trip (single, multi, etc.)")


class ParsedConstraints(BaseModel):
    """Structured interpretation of a client's insurance needs."""
    core: CoreConstraints = Field(description="age, destination, duration, employment_type, trip_type")
    interpreted_needs: list[str] = Field(description="Explicit and implicit needs (Dutch)")
    context_notes: list[str] = Field(description="Existing policies, budget, special circumstances (Dutch)")
    potential_trade_offs: list[str] = Field(description="Tensions in client situation (Dutch)")
    retrieval_aspects: list[RetrievalAspect] = Field(description="Topics to investigate, ordered by priority")


# --- Orchestrator Assessment schemas ---

class RetrievalTask(BaseModel):
    """A single retrieval task to dispatch to a retriever agent."""
    provider: str
    query: str = Field(description="Search query (English)")
    aspect: str


class ProviderStatus(BaseModel):
    """Status update for a provider during orchestration."""
    provider: str
    status: Literal["active", "dropped", "sufficient"]
    reason: str = Field(description="Explanation (Dutch)")


class CoverageLevelUpdate(BaseModel):
    """Status update for a specific coverage level within a provider."""
    provider: str
    coverage_level: str
    status: Literal["active", "dropped"]
    reason: str = ""


class AssessmentResult(BaseModel):
    """Orchestrator's assessment of current retrieval state."""
    provider_updates: list[ProviderStatus]
    coverage_level_updates: list[CoverageLevelUpdate] = Field(
        default_factory=list,
        description="Updates to individual coverage level statuses within active providers",
    )
    retrieval_tasks: list[RetrievalTask]
    proceed_to_evaluation: bool
    notes: str = Field(description="Decision reasoning (Dutch)")


# --- Retriever schemas ---

class CoverageLevelSummary(BaseModel):
    """Findings for a specific coverage level within a provider."""
    coverage_level: str
    summary: str = Field(description="What the documents say (Dutch)")
    limitations: str = Field(description="Limitations found (Dutch)")
    notable: str = Field(description="Notable conditions or exclusions (Dutch)")


class RetrievalSummary(BaseModel):
    """Summary of retrieved information for one provider-aspect combination."""
    provider: str
    aspect: str
    overall_summary: str = Field(description="Provider-level finding, not coverage-specific (Dutch)")
    coverage_level_findings: list[CoverageLevelSummary]
    information_not_found: str = Field(description="What could not be found (Dutch)")
    confidence: Literal["high", "medium", "low"]
    ambiguities: str = Field(description="Unclear or ambiguous clauses (Dutch)")


# --- Evaluator Step 1 schemas ---

class ProviderCoverageAssessment(BaseModel):
    """Qualitative assessment of a single provider-coverage combination."""
    provider: str
    coverage_level: str
    premium: float
    overall_fit: str = Field(description="How well it fits client needs (Dutch)")
    strengths: list[str] = Field(description="Positive aspects (Dutch)")
    weaknesses: list[str] = Field(description="Negative aspects (Dutch)")
    uncertainties: list[str] = Field(description="Unclear or unverified aspects (Dutch)")


class QualitativeAssessment(BaseModel):
    """Holistic assessment of all active provider-coverage combinations."""
    assessments: list[ProviderCoverageAssessment]
    cross_provider_observations: str = Field(description="Patterns across providers (Dutch)")


# --- Evaluator Step 2 schemas ---

class Recommendation(BaseModel):
    """A single insurance recommendation with reasoning."""
    provider: str
    coverage_level: str
    premium: float
    reasoning: str = Field(description="Why this is recommended (Dutch)")
    trade_offs: str = Field(description="What trade-offs were made (Dutch)")
    advantages: list[str] = Field(description="Key advantages (Dutch)")
    disadvantages: list[str] = Field(description="Key disadvantages (Dutch)")


class NotableRejection(BaseModel):
    """A provider that was considered but rejected, with explanation."""
    provider: str
    coverage_level: str
    reason: str = Field(description="Why this was rejected (Dutch)")


class FinalRecommendation(BaseModel):
    """Final output of the hierarchical recommendation system."""
    top_recommendations: list[Recommendation] = Field(description="2 best-fit recommendations")
    budget_recommendations: list[Recommendation] = Field(description="2 budget-friendly recommendations")
    notable_rejected: list[NotableRejection] = Field(description="Notable rejections worth explaining")
    overall_analysis: str = Field(description="Overall analysis and context (Dutch)")
