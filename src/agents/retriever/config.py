"""Default configuration for the retriever agent."""

import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from src.retrieval.retriever import retriever
from src.retrieval.reranker.reranker import reranker

retriever = retriever
reranker = reranker
grading_llm = ChatOpenAI(model="gpt-5-mini", temperature=0)
rewrite_llm = ChatOpenAI(model="gpt-5-mini", temperature=0)
generation_llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=1,
    google_api_key=os.getenv("GEMINI_API_KEY")  # Use GEMINI_API_KEY from .env
)