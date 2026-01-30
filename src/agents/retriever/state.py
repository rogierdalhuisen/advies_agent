"""State for the self-reflective RAG retriever graph."""

from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_core.documents import Document


class RetrieverState(BaseModel):
    """Shared state passed between nodes in the retriever graph."""

    original_query: str = ""
    current_query: str = ""
    insurance_provider: str = ""
    documents: List[Document] = Field(default_factory=list)
    evaluation_status: Literal["direct", "indirect", "miss", ""] = ""
    answer: str = ""
    retries: int = 0
    max_retries: int = 3
