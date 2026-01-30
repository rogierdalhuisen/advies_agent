"""Reranker module for re-ordering retrieved documents."""

import requests
import json
from typing import List, Tuple
from langchain_core.documents import Document

from .config import (
    RERANKER_API_URL,
    RERANKER_API_KEY,
    RERANKER_PROVIDER,
    RERANKER_MODEL
)

class RemoteReranker:
    """Independent reranker using remote inference APIs (Cross-Encoder style)."""

    def __init__(
        self, 
        api_url: str = RERANKER_API_URL, 
        api_key: str = RERANKER_API_KEY,
        provider: str = RERANKER_PROVIDER
    ):
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.provider = provider

    def rerank(self, query: str, documents: List[Document], top_n: int = 5) -> List[Document]:
        """
        Reranks a list of documents based on relevance to the query.
        """
        if not documents:
            return []

        # 1. Prepare Text Pairs
        doc_texts = [doc.page_content for doc in documents]
        
        # 2. Get Scores (Provider specific logic)
        if self.provider == "huggingface":
            scores = self._call_huggingface(query, doc_texts)
        elif self.provider == "cohere":
            scores = self._call_cohere(query, doc_texts)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        # 3. Attach scores and Sort
        for doc, score in zip(documents, scores):
            doc.metadata["rerank_score"] = score

        # Sort descending by score
        ranked_docs = sorted(
            documents, 
            key=lambda x: x.metadata.get("rerank_score", 0), 
            reverse=True
        )

        return ranked_docs[:top_n]

    def _call_huggingface(self, query: str, texts: List[str]) -> List[float]:
        """Calls HF Inference API (Standard Cross-Encoder Payload)."""
        payload = {
            "inputs": {
                "source_sentence": query,
                "sentences": texts
            }
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        # HF typically returns a flat list of scores
        return response.json()

    def _call_cohere(self, query: str, texts: List[str]) -> List[float]:
        """Calls Cohere Rerank API."""
        payload = {
            "model": RERANKER_MODEL,
            "query": query,
            "documents": texts,
            "top_n": len(texts) # Rank all, let main function slice
        }
        
        # Note: Cohere URL is standard, usually not in config unless custom endpoint
        url = "https://api.cohere.ai/v1/rerank"
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Map results back to original order (Cohere returns sorted list with indices)
        scores = [0.0] * len(texts)
        for result in data["results"]:
            scores[result["index"]] = result["relevance_score"]
            
        return scores