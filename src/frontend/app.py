"""Chainlit frontend with dynamic agent selection via ChatProfiles."""

import os

import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

from src.frontend.settings import AGENTS, AGENT_NAMES, DEFAULT_AGENT


# --- Data layer for chat history persistence ---

@cl.data_layer
def get_data_layer():
    conninfo = os.environ.get(
        "CHAINLIT_DB_URL",
        "postgresql+asyncpg://chainlit:chainlit@postgres_chainlit:5432/chainlit",
    )
    return SQLAlchemyDataLayer(conninfo=conninfo)


# --- Auto-authenticate every request (no login screen) ---

@cl.header_auth_callback
def header_auth_callback(headers: dict):
    return cl.User(identifier="dev", metadata={"role": "admin", "provider": "header"})


@cl.set_chat_profiles
async def chat_profiles():
    """Define agent profiles shown in the header dropdown."""
    return [
        cl.ChatProfile(
            name=name,
            markdown_description=config["description"],
        )
        for name, config in AGENTS.items()
    ]


@cl.on_chat_start
async def on_chat_start():
    """Initialize the selected agent and present its settings."""
    agent_name = cl.user_session.get("chat_profile") or DEFAULT_AGENT
    config = AGENTS[agent_name]
    agent = config["class"]()

    cl.user_session.set("agent_name", agent_name)
    cl.user_session.set("agent", agent)

    settings = await cl.ChatSettings(config["build_widgets"]()).send()
    for key, value in settings.items():
        cl.user_session.set(key, value)

    await cl.Message(content=f"**{agent_name}** agent ready.").send()


@cl.on_chat_resume
async def on_chat_resume(thread):
    """Restore the agent when reopening an old chat."""
    agent_name = thread.get("metadata", {}).get("agent_name", DEFAULT_AGENT)
    config = AGENTS.get(agent_name, AGENTS[DEFAULT_AGENT])
    agent = config["class"]()

    cl.user_session.set("agent_name", agent_name)
    cl.user_session.set("agent", agent)


@cl.on_settings_update
async def on_settings_update(settings):
    """Store updated provider settings."""
    for key, value in settings.items():
        cl.user_session.set(key, value)


@cl.on_message
async def on_message(message: cl.Message):
    """Stream the active agent's graph and display intermediate steps."""
    agent = cl.user_session.get("agent")
    config = AGENTS[cl.user_session.get("agent_name")]

    inputs = config["build_inputs"](message.content, cl.user_session)
    render_node = config["render_node"]
    output_key = config["output_key"]

    final_answer = ""

    async for event in agent.graph.astream(inputs, stream_mode="updates"):
        for node_name, node_output in event.items():
            if output_key in node_output:
                final_answer = node_output[output_key]

            rendered = render_node(node_name, node_output)
            if rendered:
                label, text = rendered
                async with cl.Step(name=label) as step:
                    step.output = text

    await cl.Message(content=final_answer or "No answer generated.").send()
