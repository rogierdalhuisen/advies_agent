"""Internal pipeline state for the structured retriever subgraph."""

from typing import Literal, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage


class RetrieverState(TypedDict):
    """Extends RetrieverSubState with pipeline-internal fields.

    Parent-compatible keys: provider, query, aspect, product_description, retrieval_summary, messages.
    Internal keys: documents, current_query, evaluation_status, retries.
    """

    # --- Parent-compatible keys (from RetrieverSubState) ---
    messages: list[AnyMessage]
    provider: str
    query: str
    aspect: str
    product_description: str
    retrieval_summary: dict

    # --- Pipeline-internal keys ---
    documents: list[Document]
    current_query: str
    evaluation_status: Optional[Literal["direct", "indirect", "miss"]]
    retries: int
