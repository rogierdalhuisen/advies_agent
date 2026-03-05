"""Configuration and agent registry for the Chainlit frontend."""

from chainlit.input_widget import Select, Slider

from src.agents.retriever import RetrieverAgent
from src.agents.comparer import ComparerAgent
from src.providers import ALL_PROVIDER_NAMES

INSURANCE_PROVIDERS = sorted(ALL_PROVIDER_NAMES)

DEFAULT_PROVIDER_INDEX = 0


# --- Per-agent node renderers ---
# Return (label, text) for intermediate display, or None to skip.


def _render_route_node(node_name, node_output):
    if node_name == "route":
        premium_data = node_output.get("premium_data", "")
        if premium_data:
            return ("Routing query", "Pricing query detected — using calculator tool")
        return ("Routing query", "Document retrieval query — using RAG pipeline")
    return None


def _render_retriever_node(node_name, node_output):
    result = _render_route_node(node_name, node_output)
    if result:
        return result
    if node_name == "retrieve":
        docs = node_output.get("documents", [])
        return ("Retrieving documents", f"Retrieved **{len(docs)}** documents")
    if node_name == "rerank":
        docs = node_output.get("documents", [])
        lines = []
        for i, doc in enumerate(docs, 1):
            score = doc.metadata.get("rerank_score", "n/a")
            source = doc.metadata.get("source", "unknown")
            lines.append(f"{i}. `{source}` (score: {score})")
        return ("Reranking documents", "\n".join(lines) or "No documents after reranking")
    if node_name == "grade":
        status = node_output.get("evaluation_status", "")
        return ("Grading relevance", f"Evaluation: **{status}**")
    if node_name == "rewrite":
        query = node_output.get("current_query", "")
        retries = node_output.get("retries", 0)
        return ("Rewriting query", f"Rewritten query (attempt {retries}): *{query}*")
    return None


def _render_comparer_node(node_name, node_output):
    result = _render_route_node(node_name, node_output)
    if result:
        return result
    if node_name == "retrieve_all":
        results = node_output.get("provider_results", [])
        lines = [f"- **{r.insurance_provider}**" for r in results]
        return ("Retrieving all providers", "\n".join(lines) or "Retrieving...")
    return None


# --- Agent registry ---


AGENTS = {
    "Retriever": {
        "class": RetrieverAgent,
        "description": "Stel vragen over een verzekering",
        "build_widgets": lambda: [
            Select(
                id="provider",
                label="Insurance Provider",
                values=INSURANCE_PROVIDERS,
                initial_index=DEFAULT_PROVIDER_INDEX,
            ),
            Slider(
                id="k",
                label="Documents to retrieve (k)",
                initial=15,
                min=1,
                max=50,
                step=1,
            ),
            Slider(
                id="top_n",
                label="Documents after reranking (top_n)",
                initial=5,
                min=1,
                max=20,
                step=1,
            ),
        ],
        "build_inputs": lambda query, session: {
            "original_query": query,
            "insurance_provider": session.get("provider"),
        },
        "output_key": "answer",
        "render_node": _render_retriever_node,
    },
    "Vergelijker": {
        "class": ComparerAgent,
        "description": "Vergelijk verschillende verzekeringen",
        "build_widgets": lambda: [
            Select(
                id="provider_1",
                label="Provider 1",
                values=INSURANCE_PROVIDERS,
                initial_index=0,
            ),
            Select(
                id="provider_2",
                label="Provider 2",
                values=INSURANCE_PROVIDERS,
                initial_index=1,
            ),
            Select(
                id="provider_3",
                label="Provider 3 (optional)",
                values=["none"] + INSURANCE_PROVIDERS,
                initial_index=0,
            ),
            Slider(
                id="k",
                label="Documents to retrieve (k)",
                initial=15,
                min=1,
                max=50,
                step=1,
            ),
            Slider(
                id="top_n",
                label="Documents after reranking (top_n)",
                initial=5,
                min=1,
                max=20,
                step=1,
            ),
        ],
        "build_inputs": lambda query, session: {
            "original_query": query,
            "insurance_providers": [
                p for p in [
                    session.get("provider_1"),
                    session.get("provider_2"),
                    session.get("provider_3"),
                ] if p and p != "none"
            ],
        },
        "output_key": "comparison",
        "render_node": _render_comparer_node,
    },
}

DEFAULT_AGENT = "Retriever"
AGENT_NAMES = list(AGENTS.keys())
