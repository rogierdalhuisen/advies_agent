"""Node functions for the user agent."""

import json

from langchain_core.messages import SystemMessage, HumanMessage

from ..config import opus_llm
from ..state import OrchestratorState
from ..schemas import ParsedConstraints
from .prompts import USER_AGENT_PROMPT


def user_agent_node(state: OrchestratorState) -> dict:
    """Parse user profile into structured constraints using Opus."""
    llm = opus_llm.with_structured_output(ParsedConstraints)

    response = llm.invoke([
        SystemMessage(content=USER_AGENT_PROMPT),
        HumanMessage(content=json.dumps(state["user_profile"], ensure_ascii=False, default=str)),
    ])

    return {"parsed_constraints": response.model_dump()}
