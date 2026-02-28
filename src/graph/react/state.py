"""State definition for the single ReAct agent."""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


class SingleAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_constraints: str
    insurance_providers: list[str]
    product_descriptions: str
    recommendation: str
