"""State definitions for the comparer agent."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.documents import Document


class RetrieverState(BaseModel):
    """State for a single-provider retriever subgraph."""

    original_query: str = ""
    current_query: str = ""
    insurance_provider: str = ""
    documents: List[Document] = Field(default_factory=list)
    evaluation_status: Optional[Literal["direct", "indirect", "miss"]] = None
    answer: str = ""
    premium_data: str = ""
    retries: int = 0


class ProviderResult(BaseModel):
    """Result from a single provider's retrieval."""

    insurance_provider: str = ""
    answer: str = ""


class ComparerState(BaseModel):
    """Top-level state for comparing across multiple insurance providers."""

    original_query: str = ""
    insurance_providers: List[str] = Field(default_factory=list)
    provider_results: List[ProviderResult] = Field(default_factory=list)
    comparison: str = ""
    premium_data: str = ""
