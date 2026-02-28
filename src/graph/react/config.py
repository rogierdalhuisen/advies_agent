"""Configuration for the single ReAct agent."""

from pathlib import Path

from langchain_openai import ChatOpenAI

from src.agents.retriever import RetrieverAgent
from src.config import DATA_DIR


# Main reasoning LLM
reasoning_llm = ChatOpenAI(model="gpt-5.2", temperature=0.3)

# Retriever agent instance (reuses its own internal config)
retriever_agent = RetrieverAgent()

# Static product description directory
STATIC_FILES_DIR = DATA_DIR / "static_agent_files"


def load_product_descriptions() -> str:
    """Load and concatenate all static product description files."""
    descriptions = []
    for md_file in sorted(STATIC_FILES_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8").strip()
        descriptions.append(content)
    return "\n\n---\n\n".join(descriptions)
