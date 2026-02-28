"""State for the self-reflective RAG retriever graph."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.documents import Document


class RetrieverState(BaseModel):
    """Shared state passed between nodes in the retriever graph."""

    original_query: str = ""
    current_query: str = ""
    insurance_provider: str = ""
    documents: List[Document] = Field(default_factory=list)
    evaluation_status: Optional[Literal["direct", "indirect", "miss"]] = None
    answer: str = ""
    retries: int = 0
    premium_data: str = ""
