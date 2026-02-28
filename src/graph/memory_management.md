# Memory Management Notes

- Static insurance description files (1)
- Online retrieved passages (2)
- Decision Summaries (3)

## Single Agent

(1) In systemprompt | Simpler than in state, and prevents from using tool calls to obtain correct state info. | Costs a bit more tokens per prompt
(2)

Agent

## Orchestrator system

(1) In systemprompt Orchastrator | Simpler than in state, and prevents from using tool calls to obtain correct state info. | Costs a bit more tokens per prompt
(2, 3) Orchestrator receives summaries and stores in prompt
All agents communicate together using the state.

## user-item collabaration

(1) in each item-agent system prompt
(2) Only in the independent agents state

You spawn a user agent instance + item agent instance per product, each pair runs in its own sub-graph with its own local state. The user-item dialogue (messages back and forth, retrieved documents, constraint checks) lives in that local state. When the dialogue concludes, a structured summary (your Option B) gets written back to the parent graph's state, where the final decision agent can read all summaries.

Parent graph state: {
user_constraints: ...,
product_candidates: [...],
dialogue_summaries: {product_id: summary, ...}, ← Option B summaries land here
final_recommendation: ...
}

Sub-graph (per product) state: {
user_constraints: ..., ← copied in from parent
product_description: ..., ← item agent identity
dialogue_history: [...], ← user-item messages
retrieved_documents: [...], ← from retriever calls
summary: ... ← structured output, returned to parent
}
