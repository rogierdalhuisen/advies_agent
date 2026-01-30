"""Reranker module for re-ordering retrieved documents via SiliconFlow."""

import requests
import json
from typing import List
from langchain_core.documents import Document

from .config import (
    RERANKER_API_URL,
    RERANKER_API_KEY,
    RERANKER_PROVIDER,
    RERANKER_MODEL
)

class Reranker:
    """Independent reranker using SiliconFlow's Qwen Reranker."""

    def __init__(
        self, 
        api_url: str = RERANKER_API_URL, 
        api_key: str = RERANKER_API_KEY,
        model: str = RERANKER_MODEL
    ):
        self.api_url = api_url
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def rerank(self, query: str, documents: List[Document], top_n: int = 5) -> List[Document]:
        """
        Reranks a list of documents based on relevance to the query.
        """
        if not documents:
            return []

        # 1. Prepare Text List
        doc_texts = [doc.page_content for doc in documents]
        
        # 2. Call SiliconFlow API
        try:
            scores = self._call_siliconflow(query, doc_texts)
        except Exception as e:
            print(f"Reranking failed: {e}. Returning original order.")
            return documents[:top_n]

        # 3. Attach scores and Sort
        # SiliconFlow returns scores in a specific order, we map them back
        for doc, score in zip(documents, scores):
            doc.metadata["rerank_score"] = score

        # Sort descending by score
        ranked_docs = sorted(
            documents, 
            key=lambda x: x.metadata.get("rerank_score", 0), 
            reverse=True
        )

        return ranked_docs[:top_n]

    def _call_siliconflow(self, query: str, texts: List[str]) -> List[float]:
        """Calls SiliconFlow Rerank API."""
        payload = {
            "model": self.model,
            "query": query,
            "documents": texts,
            "return_documents": False,
            "top_n": len(texts)  # Score all documents provided
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # The API returns a list of results with indices:
        # { "results": [ {"index": 0, "relevance_score": 0.9}, {"index": 2, ...} ] }
        # We need to map these back to the original list order [doc0, doc1, doc2]
        
        scores = [0.0] * len(texts)
        if "results" in data:
            for item in data["results"]:
                idx = item.get("index")
                score = item.get("relevance_score")
                if idx is not None and 0 <= idx < len(scores):
                    scores[idx] = score
                    
        return scores
    
reranker = Reranker()