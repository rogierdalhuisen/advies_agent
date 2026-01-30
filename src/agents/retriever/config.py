"""Configuration for the retriever agent graph."""

from langchain_openai import ChatOpenAI

from src.retrieval.retriever import InsuranceRetriever
from src.retrieval.reranker.reranker import Reranker

# Components
retriever = InsuranceRetriever()
reranker = Reranker()

# LLMs — swap these to use a different model for any step
grading_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
rewrite_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
generation_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
