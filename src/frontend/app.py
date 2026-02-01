"""Chainlit frontend with dynamic agent selection."""

import chainlit as cl
from chainlit.input_widget import Select

from src.frontend.settings import AGENTS, AGENT_NAMES, DEFAULT_AGENT


def _build_widgets(agent_name: str) -> list:
    """Build the full widget list: agent selector + agent-specific widgets."""
    agent_select = Select(
        id="agent",
        label="Agent",
        values=AGENT_NAMES,
        initial_index=AGENT_NAMES.index(agent_name),
    )
    return [agent_select] + AGENTS[agent_name]["build_widgets"]()


RESERVED_KEYS = {"agent", "agent_name"}


def _store_settings(settings: dict):
    """Persist widget values into user_session, skipping reserved keys."""
    for key, value in settings.items():
        if key not in RESERVED_KEYS:
            cl.user_session.set(key, value)


@cl.on_chat_start
async def on_chat_start():
    """Initialize the default agent and present settings."""
    agent_name = DEFAULT_AGENT
    agent = AGENTS[agent_name]["class"]()

    cl.user_session.set("agent_name", agent_name)
    cl.user_session.set("agent", agent)

    settings = await cl.ChatSettings(_build_widgets(agent_name)).send()
    _store_settings(settings)

    await cl.Message(content=f"**{agent_name}** agent ready.").send()


@cl.on_settings_update
async def on_settings_update(settings):
    """Handle setting changes; re-send widgets when agent type changes."""
    new_agent_name = settings.get("agent", cl.user_session.get("agent_name"))
    old_agent_name = cl.user_session.get("agent_name")

    if new_agent_name != old_agent_name:
        agent = AGENTS[new_agent_name]["class"]()
        cl.user_session.set("agent_name", new_agent_name)
        cl.user_session.set("agent", agent)

        new_settings = await cl.ChatSettings(_build_widgets(new_agent_name)).send()
        _store_settings(new_settings)

        await cl.Message(content=f"Switched to **{new_agent_name}** agent.").send()
    else:
        _store_settings(settings)


@cl.on_message
async def on_message(message: cl.Message):
    """Dispatch the query to the active agent and send the result."""
    agent_name = cl.user_session.get("agent_name")
    agent = cl.user_session.get("agent")
    config = AGENTS[agent_name]

    inputs = config["build_inputs"](message.content, cl.user_session)
    result = await agent.graph.ainvoke(inputs)

    answer = result.get(config["output_key"], "No answer generated.")
    await cl.Message(content=answer).send()
