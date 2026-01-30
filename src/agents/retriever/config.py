"""Default configuration for the retriever agent."""

from langchain_openai import ChatOpenAI

from src.retrieval.retriever import InsuranceRetriever
from src.retrieval.reranker.reranker import Reranker

DEFAULTS = {
    "retriever": InsuranceRetriever,
    "reranker": Reranker,
    "grading_llm": lambda: ChatOpenAI(model="gpt-4o-mini", temperature=0),
    "rewrite_llm": lambda: ChatOpenAI(model="gpt-4o-mini", temperature=0),
    "generation_llm": lambda: ChatOpenAI(model="gpt-4o-mini", temperature=0),
}
