name: langgraph-agent-structure
description: Design structured LangGraph agents and subgraphs with modular components

---

# LangGraph Agent Structure

When building LangGraph agents or subgraphs, follow a structured modular design.

## Standard layout

agent_name/
├── **init**.py
├── config.py
├── graphs.py
├── nodes.py
├── state.py
└── prompts.py

Responsibilities:

config.py
dependency providers (LLMs, retrievers, rerankers)

state.py
graph state schema

nodes.py
node logic and node factories

graphs.py
graph wiring using StateGraph

prompts.py
prompts only

## Graph design principles

Prefer deterministic pipelines:

retrieve → rerank → grade → rewrite → summarize

Routing logic should be simple and explicit.

Example:

retrieve → rerank → grade  
grade → summarize OR rewrite

## Implementation guidelines

Prefer node factories:

make_retrieve(...)
make_rerank(...)
make_grade(...)

Provide a builder:

build_retriever_subgraph()

This returns a compiled graph ready to invoke.

## Code simplicity

Keep the pipeline logic readable and small.

Avoid unnecessary abstraction layers.

Focus on clarity of the workflow.
