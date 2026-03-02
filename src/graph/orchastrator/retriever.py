"""Retriever ReAct subgraph for the hierarchical orchestrator.

Each retriever instance investigates one aspect for one provider,
using retrieve_and_rerank to search documents and submit_summary to report findings.
"""

import json

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from .state import RetrieverSubState
from .schemas import RetrievalSummary
from .config import gpt5_2_llm, insurance_retriever, reranker
from .prompts import RETRIEVER_AGENT_PROMPT_TEMPLATE


# --- Tools ---

@tool
def retrieve_and_rerank(query: str, provider: str) -> str:
    """Retrieve and rerank insurance policy documents.

    Searches the vector store for documents matching the query, filtered by provider,
    then reranks results for relevance.

    Args:
        query: Search query in English.
        provider: Insurance provider folder name.

    Returns:
        Formatted text of top relevant document passages.
    """
    results = insurance_retriever.retrieve_company_docs(query, provider, k=25)

    if not results:
        return "Geen documenten gevonden voor deze zoekopdracht."

    # Extract documents from (doc, score) tuples
    docs = [doc for doc, _score in results]

    # Rerank
    reranked = reranker.rerank(query, docs, top_n=8)

    # Format results
    formatted = []
    for i, doc in enumerate(reranked, 1):
        context_text = insurance_retriever.format_document_with_context(doc)
        formatted.append(f"[{i}] {context_text}")

    return "\n\n---\n\n".join(formatted)


@tool
def submit_summary(
    provider: str,
    aspect: str,
    overall_summary: str,
    coverage_level_findings: list[dict],
    information_not_found: str,
    confidence: str,
    ambiguities: str,
) -> str:
    """Submit the retrieval summary for this provider-aspect investigation.

    Call this when you have gathered enough information (or exhausted search options).

    Args:
        provider: Insurance provider name.
        aspect: The aspect that was investigated.
        overall_summary: Provider-level finding (Dutch).
        coverage_level_findings: List of dicts with coverage_level, summary, limitations, notable (Dutch).
        information_not_found: What could not be found (Dutch).
        confidence: "high", "medium", or "low".
        ambiguities: Unclear or ambiguous clauses (Dutch).

    Returns:
        Confirmation message.
    """
    # The summary is captured from the tool call arguments by the graph
    return "Samenvatting ingediend. Onderzoek afgerond."


RETRIEVER_TOOLS = [retrieve_and_rerank, submit_summary]


# --- Subgraph nodes ---

def _build_system_message(state: RetrieverSubState) -> SystemMessage:
    """Build the retriever agent system prompt from state."""
    prompt = RETRIEVER_AGENT_PROMPT_TEMPLATE.format(
        aspect=state["aspect"],
        provider=state["provider"],
        product_description=state.get("product_description", "Geen beschrijving beschikbaar."),
    )
    return SystemMessage(content=prompt)


def retriever_agent_node(state: RetrieverSubState) -> dict:
    """Call the retriever LLM with tools."""
    llm_with_tools = gpt5_2_llm.bind_tools(RETRIEVER_TOOLS)

    system_msg = _build_system_message(state)
    messages = [system_msg] + state["messages"]

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def check_submit_and_extract(state: RetrieverSubState) -> dict:
    """Check if submit_summary was called and extract the summary into state."""
    messages = state["messages"]

    # Walk backwards to find the last AI message with tool calls
    for msg in reversed(messages):
        if not isinstance(msg, AIMessage) or not getattr(msg, "tool_calls", None):
            continue
        for tc in msg.tool_calls:
            if tc["name"] == "submit_summary":
                args = tc["args"]
                try:
                    # GPT models may return empty strings instead of empty lists
                    findings = args.get("coverage_level_findings", [])
                    if not isinstance(findings, list):
                        findings = []
                    confidence_raw = str(args.get("confidence", "low")).lower()
                    summary = RetrievalSummary(
                        provider=args.get("provider", state["provider"]),
                        aspect=args.get("aspect", state["aspect"]),
                        overall_summary=args.get("overall_summary", ""),
                        coverage_level_findings=findings,
                        information_not_found=args.get("information_not_found", ""),
                        confidence=confidence_raw if confidence_raw in ("high", "medium", "low") else "low",
                        ambiguities=args.get("ambiguities", ""),
                    )
                    return {"retrieval_summary": summary.model_dump()}
                except Exception as e:
                    # Fallback: don't let a parsing error kill the whole graph
                    print(f"[retriever] Warning: failed to parse submit_summary args: {e}")
                    fallback = RetrievalSummary(
                        provider=state["provider"],
                        aspect=state["aspect"],
                        overall_summary=args.get("overall_summary", "Samenvatting kon niet worden verwerkt."),
                        coverage_level_findings=[],
                        information_not_found="Parsing van retriever output is mislukt.",
                        confidence="low",
                        ambiguities=str(e),
                    )
                    return {"retrieval_summary": fallback.model_dump()}

    return {}


def _should_continue(state: RetrieverSubState) -> str:
    """Route after tool execution: check if submit_summary was called or max iterations reached."""
    messages = state["messages"]

    # Check if submit_summary was called
    for msg in reversed(messages):
        if not isinstance(msg, AIMessage) or not getattr(msg, "tool_calls", None):
            continue
        for tc in msg.tool_calls:
            if tc["name"] == "submit_summary":
                return "extract_and_end"
        break  # Only check the most recent AI message

    # Count tool call rounds (AI messages with tool calls)
    tool_rounds = sum(
        1 for m in messages
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None)
    )

    if tool_rounds >= 5:
        return "force_end"

    return "continue"


def force_submit_node(state: RetrieverSubState) -> dict:
    """Force a summary when max iterations reached without submit_summary."""
    summary = RetrievalSummary(
        provider=state["provider"],
        aspect=state["aspect"],
        overall_summary="Maximaal aantal zoekpogingen bereikt zonder volledige samenvatting.",
        coverage_level_findings=[],
        information_not_found="Onderzoek was niet volledig afgerond binnen het maximale aantal iteraties.",
        confidence="low",
        ambiguities="Niet beoordeeld door geforceerde afronding.",
    )
    return {"retrieval_summary": summary.model_dump()}


# --- Build subgraph ---

def build_retriever_subgraph():
    """Build and compile the retriever ReAct subgraph."""
    workflow = StateGraph(RetrieverSubState)

    workflow.add_node("agent", retriever_agent_node)
    workflow.add_node("tools", ToolNode(RETRIEVER_TOOLS))
    workflow.add_node("extract_summary", check_submit_and_extract)
    workflow.add_node("force_submit", force_submit_node)

    workflow.add_edge(START, "agent")

    # After agent: check if it wants to call tools or is done
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
    )

    # After tools: check if submit_summary was called
    workflow.add_conditional_edges(
        "tools",
        _should_continue,
        {
            "extract_and_end": "extract_summary",
            "force_end": "force_submit",
            "continue": "agent",
        },
    )

    workflow.add_edge("extract_summary", END)
    workflow.add_edge("force_submit", END)

    return workflow.compile()


retriever_subgraph = build_retriever_subgraph()
