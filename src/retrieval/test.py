"""
Routing Agentic Workflow with Custom Qdrant Tools
Following LangGraph tutorial structure
"""

from typing import Literal, TypedDict, Annotated
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, ToolMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
import operator
from pydantic import BaseModel, Field

# Assuming you have these imports from your code
# from qdrant_client import QdrantClient
# from your_module import QdrantVectorStore, RetrievalMode, embeddings, sparse_embeddings
# from your_module import create_company_search_tool, create_all_companies_dense_search_tool

# Initialize your Qdrant client and tools (your existing code)

client = QdrantClient(host=QDRANT_HOST)
vector_store = QdrantVectorStore(
    client=client,
    collection_name="dekkingen",
    embedding=embeddings,
    sparse_embedding=sparse_embeddings,
    retrieval_mode=RetrievalMode.DENSE,
    vector_name="dense",
    sparse_vector_name="sparse",
)
search_company_coverage_tool = create_company_search_tool(vector_store)
search_all_coverage_dense_tool = create_all_companies_dense_search_tool(vector_store)
tools = [search_company_coverage_tool, search_all_coverage_dense_tool]
llm_with_tools = llm.bind_tools(tools)



# ============================================================================
# OPTION 2: ROUTING WORKFLOW (Routes queries to specific tool-based paths)
# ============================================================================

class RouteDecision(BaseModel):
    """Schema for routing decision"""
    route: Literal["company_specific", "all_companies", "general"] = Field(
        description="Route the query to appropriate search type"
    )
    reasoning: str = Field(
        description="Explanation for the routing decision"
    )


class RoutingState(MessagesState):
    """State for routing workflow"""
    route_decision: str = ""
    search_results: list = []


def create_routing_workflow(llm, tools):
    """
    Creates a routing workflow that decides which tool to use based on query type
    """
    # Create router with structured output
    router_llm = llm.with_structured_output(RouteDecision)
    
    # Bind individual tools to LLM for each route
    company_tool = tools[0]  # search_company_coverage_tool
    all_companies_tool = tools[1]  # search_all_coverage_dense_tool
    
    company_llm = llm.bind_tools([company_tool])
    all_companies_llm = llm.bind_tools([all_companies_tool])
    
    # Create tool nodes for each route
    company_tool_node = ToolNode([company_tool])
    all_companies_tool_node = ToolNode([all_companies_tool])
    
    # Router node
    def router(state: RoutingState):
        """Analyzes the query and decides which search path to take"""
        messages = state["messages"]
        
        routing_prompt = SystemMessage(
            content="""Analyze the user query and decide the best search approach:
            - 'company_specific': For queries about a specific company's coverage
            - 'all_companies': For queries comparing or searching across all companies
            - 'general': For general questions that don't need coverage search"""
        )
        
        decision = router_llm.invoke([routing_prompt] + messages)
        return {"route_decision": decision.route}
    
    # Company-specific search node
    def company_search(state: RoutingState):
        """Handles company-specific coverage searches"""
        messages = state["messages"]
        response = company_llm.invoke(
            [SystemMessage(content="Search for company-specific coverage information.")] + messages
        )
        return {"messages": [response]}
    
    # All companies search node
    def all_companies_search(state: RoutingState):
        """Handles searches across all companies"""
        messages = state["messages"]
        response = all_companies_llm.invoke(
            [SystemMessage(content="Search across all companies for coverage information.")] + messages
        )
        return {"messages": [response]}
    
    # General response node
    def general_response(state: RoutingState):
        """Handles general queries without tool usage"""
        messages = state["messages"]
        response = llm.invoke(
            [SystemMessage(content="Provide a helpful response based on the query.")] + messages
        )
        return {"messages": [response]}
    
    # Synthesizer node (combines results)
    def synthesizer(state: RoutingState):
        """Synthesizes the final response"""
        messages = state["messages"]
        
        # Create final response based on search results
        final_response = llm.invoke(
            [SystemMessage(content="Synthesize the search results into a clear, comprehensive answer.")] + messages
        )
        return {"messages": [final_response]}
    
    # Route decision function
    def route_query(state: RoutingState):
        """Routes based on the decision made by router"""
        return state["route_decision"]
    
    # Check if tool was called
    def check_tool_call(state: RoutingState) -> Literal["tools", "synthesizer"]:
        """Check if the last message contains tool calls"""
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "synthesizer"
    
    # Build the workflow
    workflow = StateGraph(RoutingState)
    
    # Add nodes
    workflow.add_node("router", router)
    workflow.add_node("company_search", company_search)
    workflow.add_node("all_companies_search", all_companies_search)
    workflow.add_node("general_response", general_response)
    workflow.add_node("company_tools", company_tool_node)
    workflow.add_node("all_companies_tools", all_companies_tool_node)
    workflow.add_node("synthesizer", synthesizer)
    
    # Add edges
    workflow.add_edge(START, "router")
    
    # Router conditional edges
    workflow.add_conditional_edges(
        "router",
        route_query,
        {
            "company_specific": "company_search",
            "all_companies": "all_companies_search",
            "general": "general_response"
        }
    )
    
    # Tool conditional edges for company search
    workflow.add_conditional_edges(
        "company_search",
        check_tool_call,
        {
            "tools": "company_tools",
            "synthesizer": "synthesizer"
        }
    )
    
    # Tool conditional edges for all companies search
    workflow.add_conditional_edges(
        "all_companies_search",
        check_tool_call,
        {
            "tools": "all_companies_tools",
            "synthesizer": "synthesizer"
        }
    )
    
    # Direct edges
    workflow.add_edge("company_tools", "synthesizer")
    workflow.add_edge("all_companies_tools", "synthesizer")
    workflow.add_edge("general_response", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    # Compile
    app = workflow.compile()
    
    return app




# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def main():
    """
    Example of how to use the routing workflows
    """
    # Assuming you have your LLM and tools initialized
    # from langchain_openai import ChatOpenAI
    # llm = ChatOpenAI(model="gpt-4")
    
    # Your existing code:
    """
    client = QdrantClient(host=QDRANT_HOST)
    vector_store = QdrantVectorStore(
        client=client,
        collection_name="dekkingen",
        embedding=embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.DENSE,
        vector_name="dense",
        sparse_vector_name="sparse",
    )
    search_company_coverage_tool = create_company_search_tool(vector_store)
    search_all_coverage_dense_tool = create_all_companies_dense_search_tool(vector_store)
    tools = [search_company_coverage_tool, search_all_coverage_dense_tool]
    """
    
    # Choose one of the workflow options:
    
    # Option 1: Basic Agent
    # agent = create_basic_agent_with_tools(llm, tools)
    
    # Option 2: Full Routing Workflow
    # agent = create_routing_workflow(llm, tools)
    
    # Option 3: Simple Routing Agent
    # agent = create_simple_routing_agent(llm, tools)
    
    # Example usage:
    """
    # For company-specific query
    response = agent.invoke({
        "messages": [HumanMessage(content="What coverage does Company X have?")]
    })
    
    # For all companies query
    response = agent.invoke({
        "messages": [HumanMessage(content="Compare coverage across all companies")]
    })
    
    # Stream responses
    for chunk in agent.stream(
        {"messages": [HumanMessage(content="Find coverage information")]},
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()
    """
    
    print("Workflow created successfully!")


if __name__ == "__main__":
    main()