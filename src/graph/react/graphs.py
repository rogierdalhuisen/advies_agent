"""Single ReAct agent for insurance recommendation using a manual StateGraph loop."""

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage

from .state import SingleAgentState
from .prompts import build_system_prompt
from .config import reasoning_llm, retriever_agent, load_product_descriptions
from .tools import make_retriever_tool
from src.tools import calculate_premiums


class SingleReActAgent:
    """Single autonomous agent that retrieves and reasons about insurance products.

    Uses a manual StateGraph ReAct loop: agent calls tools in a loop until
    it produces a final answer (no more tool calls).
    """

    def __init__(self):
        self.llm = reasoning_llm
        self.retriever_tool = make_retriever_tool(retriever_agent)
        self.tools = [self.retriever_tool, calculate_premiums]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.product_descriptions = load_product_descriptions()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the ReAct StateGraph: agent <-> tools loop."""
        workflow = StateGraph(SingleAgentState)

        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
        )
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def _call_model(self, state: SingleAgentState):
        """Invoke the LLM with system prompt + message history."""
        system_msg = SystemMessage(content=build_system_prompt(state))
        messages = [system_msg] + state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def invoke(
        self,
        user_constraints: str,
        insurance_providers: list[str],
    ) -> dict:
        """Run the agent end-to-end.

        Args:
            user_constraints: Natural language description of client needs.
            insurance_providers: List of provider folder names to consider.

        Returns:
            Final state dict with 'recommendation' extracted from last AI message.
        """
        initial_state = {
            "messages": [HumanMessage(content=user_constraints)],
            "user_constraints": user_constraints,
            "insurance_providers": insurance_providers,
            "product_descriptions": self.product_descriptions,
            "recommendation": "",
        }

        result = self.graph.invoke(initial_state)

        # Extract recommendation from the last AI message
        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and msg.content and not getattr(msg, "tool_calls", None):
                result["recommendation"] = msg.content
                break

        return result
