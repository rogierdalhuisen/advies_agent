"""Chainlit frontend for testing agents."""

import chainlit as cl
from chainlit.input_widget import Select

from src.agents.retriever import RetrieverAgent
from src.frontend.settings import INSURANCE_PROVIDERS, DEFAULT_PROVIDER_INDEX


# Display names for graph nodes shown as intermediate steps
NODE_LABELS = {
    "retrieve": "Retrieving documents",
    "rerank": "Reranking documents",
    "grade": "Grading relevance",
    "rewrite": "Rewriting query",
    "generate": "Generating answer",
}


@cl.on_chat_start
async def on_chat_start():
    """Initialize the retriever agent and present settings."""
    agent = RetrieverAgent()
    cl.user_session.set("agent", agent)
    cl.user_session.set("insurance_provider", INSURANCE_PROVIDERS[DEFAULT_PROVIDER_INDEX])

    settings = await cl.ChatSettings([
        Select(
            id="insurance_provider",
            label="Insurance Provider",
            values=INSURANCE_PROVIDERS,
            initial_index=DEFAULT_PROVIDER_INDEX,
        ),
    ]).send()

    provider = settings["insurance_provider"]
    cl.user_session.set("insurance_provider", provider)
    await cl.Message(content=f"Retriever agent ready. Provider: **{provider}**").send()


@cl.on_settings_update
async def on_settings_update(settings):
    """Update session when user changes settings."""
    provider = settings["insurance_provider"]
    cl.user_session.set("insurance_provider", provider)
    await cl.Message(content=f"Provider changed to: **{provider}**").send()


@cl.on_message
async def on_message(message: cl.Message):
    """Run the retriever agent and display intermediate steps."""
    agent: RetrieverAgent = cl.user_session.get("agent")
    provider = cl.user_session.get("insurance_provider")

    inputs = {
        "original_query": message.content,
        "insurance_provider": provider,
    }

    final_answer = ""

    async for event in agent.graph.astream(inputs, stream_mode="updates"):
        for node_name, node_output in event.items():
            label = NODE_LABELS.get(node_name, node_name)

            if node_name == "generate":
                final_answer = node_output.get("answer", "")
                async with cl.Step(name=label) as step:
                    step.output = final_answer

            elif node_name == "retrieve":
                docs = node_output.get("documents", [])
                async with cl.Step(name=label) as step:
                    step.output = f"Retrieved **{len(docs)}** documents"

            elif node_name == "rerank":
                docs = node_output.get("documents", [])
                doc_lines = []
                for i, doc in enumerate(docs, 1):
                    score = doc.metadata.get("rerank_score", "n/a")
                    source = doc.metadata.get("source", "unknown")
                    doc_lines.append(f"{i}. `{source}` (score: {score})")
                async with cl.Step(name=label) as step:
                    step.output = "\n".join(doc_lines) if doc_lines else "No documents after reranking"

            elif node_name == "grade":
                status = node_output.get("evaluation_status", "")
                async with cl.Step(name=label) as step:
                    step.output = f"Evaluation: **{status}**"

            elif node_name == "rewrite":
                new_query = node_output.get("current_query", "")
                retries = node_output.get("retries", 0)
                async with cl.Step(name=label) as step:
                    step.output = f"Rewritten query (attempt {retries}): *{new_query}*"

    await cl.Message(content=final_answer or "No answer generated.").send()
