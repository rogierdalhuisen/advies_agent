"""Configuration for the hierarchical orchestrator."""

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from src.config import DATA_DIR
from src.retrieval.retriever import InsuranceRetriever
from src.retrieval.reranker.reranker import Reranker


# Opus for orchestrator, user agent, and evaluators
opus_llm = ChatAnthropic(model="claude-opus-4-6", temperature=0.3)

#trade off llm
tradeoff_llm = ChatOpenAI(model="gpt-5.2", temperature=0.3)

# GPT-5.2 for retriever summarization
summary_llm = ChatOpenAI(model="gpt-5.2", temperature=0.3)

# Lightweight models for retriever pipeline (grading and rewriting)
grading_llm = ChatOpenAI(model="gpt-5-mini-2025-08-07", temperature=0)
rewrite_llm = ChatOpenAI(model="gpt-5-mini-2025-08-07", temperature=0.3)

# Shared retrieval components
insurance_retriever = InsuranceRetriever()
reranker = Reranker()

# Static product description directory
STATIC_FILES_DIR = DATA_DIR / "static_agent_files"


def load_product_descriptions() -> dict[str, str]:
    """Load static product descriptions as a dict keyed by provider name.

    Returns:
        Dict mapping provider name (filename without .md) to markdown content.
    """
    descriptions = {}
    for md_file in sorted(STATIC_FILES_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8").strip()
        if content:
            descriptions[md_file.stem] = content
    return descriptions
