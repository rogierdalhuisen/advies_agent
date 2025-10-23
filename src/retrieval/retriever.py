"""
Retrieval module for querying insurance coverage (dekkingen) documents.

This module provides flexible retrieval capabilities with support for:
- Semantic search (vector similarity)
- Hybrid search (semantic + keyword)
- Configurable number of results
- Metadata filtering (by company, document, etc.)

The retriever interfaces with the Qdrant vector store populated by the
ingestion pipeline and returns ranked results with full metadata.

Usage:
    from src.retrieval.retriever import DekkingenRetriever, RetrievalMethod, create_retriever

    # Option 1: Use custom RetrievalResult objects
    retriever = create_retriever(
        collection_name="dekkingen",
        method=RetrievalMethod.SEMANTIC,
        top_k=5
    )
    results = retriever.retrieve("What is covered by travel insurance?")

    # Option 2: Get LangChain Documents (production-safe)
    documents = retriever.get_langchain_documents("What is covered by travel insurance?")
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from pydantic import SecretStr
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from src.config import QDRANT_HOST, GEMINI_API_KEY


# ==================== CONFIGURATION ====================

COLLECTION_NAME = "dekkingen"
EMBEDDING_MODEL_NAME = "models/embedding-001"
DEFAULT_TOP_K = 5
DEFAULT_SCORE_THRESHOLD = 0.0  # Minimum similarity score (0-1)

# =======================================================


class RetrievalMethod(Enum):
    """Available retrieval methods."""
    SEMANTIC = "semantic"  # Pure vector similarity search
    HYBRID = "hybrid"      # Semantic + keyword search (future implementation)


@dataclass
class RetrievalResult:
    """Structured result from retrieval operation."""
    content: str
    score: float
    metadata: Dict[str, Any]

    def __repr__(self) -> str:
        company = self.metadata.get("company", "Unknown")
        doc_name = self.metadata.get("document_name", "Unknown")
        return f"RetrievalResult(score={self.score:.3f}, company={company}, doc={doc_name})"


class DekkingenRetriever:
    """
    Configurable retriever for insurance coverage documents.

    Supports multiple retrieval methods and filtering options.
    Designed for easy integration into LangChain/LangGraph workflows.
    """

    def __init__(
        self,
        collection_name: str,
        method: RetrievalMethod = RetrievalMethod.SEMANTIC,
        top_k: int = DEFAULT_TOP_K,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
        qdrant_url: str = QDRANT_HOST,
        embedding_model: str = EMBEDDING_MODEL_NAME,
    ):
        """
        Initialize the retriever.

        Args:
            collection_name: Qdrant collection name (required)
            method: Retrieval method to use (semantic or hybrid)
            top_k: Number of top results to return
            score_threshold: Minimum similarity score for results (0-1)
            qdrant_url: Qdrant instance URL
            embedding_model: Name of the embedding model
        """
        self.method = method
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.collection_name = collection_name
        self.qdrant_url = qdrant_url

        # Initialize embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=SecretStr(GEMINI_API_KEY) if GEMINI_API_KEY else None
        )

        # Initialize Qdrant client
        self.client = QdrantClient(url=qdrant_url)

        # Initialize vector store
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.embeddings,
        )

    def retrieve(
        self,
        query: str,
        company_filter: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a given query.

        Args:
            query: Search query string
            company_filter: Optional filter by company name
            top_k: Override default top_k for this query

        Returns:
            List of RetrievalResult objects sorted by relevance
        """
        k = top_k if top_k is not None else self.top_k

        if self.method == RetrievalMethod.SEMANTIC:
            return self._semantic_search(query, company_filter, k)
        elif self.method == RetrievalMethod.HYBRID:
            return self._hybrid_search(query, company_filter, k)
        else:
            raise ValueError(f"Unsupported retrieval method: {self.method}")

    def _semantic_search(
        self,
        query: str,
        company_filter: Optional[str],
        k: int,
    ) -> List[RetrievalResult]:
        """
        Perform semantic similarity search using vector embeddings.

        Args:
            query: Search query string
            company_filter: Optional filter by company name
            k: Number of results to return

        Returns:
            List of RetrievalResult objects
        """
        # Build metadata filter if company is specified
        qdrant_filter = None
        if company_filter:
            qdrant_filter = Filter(
                must=[
                    FieldCondition(
                        key="metadata.company",
                        match=MatchValue(value=company_filter)
                    )
                ]
            )

        # Perform similarity search with scores
        results = self.vector_store.similarity_search_with_score(
            query,
            k=k,
            filter=qdrant_filter
        )

        # Convert to RetrievalResult objects and filter by score threshold
        retrieval_results = []
        for doc, score in results:
            # Qdrant returns distance, convert to similarity (1 - distance for cosine)
            similarity_score = 1 - score if score < 1 else score

            if similarity_score >= self.score_threshold:
                retrieval_results.append(
                    RetrievalResult(
                        content=doc.page_content,
                        score=similarity_score,
                        metadata=doc.metadata,
                    )
                )

        return retrieval_results

    def _hybrid_search(
        self,
        query: str,
        company_filter: Optional[str],
        k: int,
    ) -> List[RetrievalResult]:
        """
        Perform hybrid search combining semantic and keyword search.

        This is a placeholder for future implementation.
        Qdrant supports hybrid search via scroll + filter combinations.

        Args:
            query: Search query string
            company_filter: Optional filter by company name
            k: Number of results to return

        Returns:
            List of RetrievalResult objects
        """
        # TODO: Implement hybrid search when needed
        # For now, fall back to semantic search
        print("Warning: Hybrid search not yet implemented, using semantic search")
        return self._semantic_search(query, company_filter, k)

    def get_langchain_documents(
        self,
        query: str,
        company_filter: Optional[str] = None,
        top_k: Optional[int] = None
    ):
        """
        Retrieve documents in LangChain Document format.

        This method directly returns LangChain Document objects, suitable for
        use in RAG chains and LangGraph agents.

        Args:
            query: Search query string
            company_filter: Optional filter by company name
            top_k: Override default top_k for this query

        Returns:
            List of LangChain Document objects with similarity scores in metadata
        """
        from langchain_core.documents import Document

        # Get results using our reliable retrieve method
        results = self.retrieve(query, company_filter, top_k)

        # Convert to LangChain Document format
        documents = []
        for result in results:
            doc = Document(
                page_content=result.content,
                metadata={
                    **result.metadata,
                    "similarity_score": result.score
                }
            )
            documents.append(doc)

        return documents

    def as_retriever_tool(self, name: str = "search_dekkingen", description: Optional[str] = None):
        """
        Convert retriever to a LangChain tool for use in LangGraph agents.

        This creates a tool that agents can dynamically invoke to search insurance
        coverage documents.

        Args:
            name: Name of the tool (default: "search_dekkingen")
            description: Optional tool description for the agent

        Returns:
            LangChain Tool that can be used with bind_tools() or in agent workflows
        """
        from langchain_core.tools import tool

        if description is None:
            description = (
                "Search insurance coverage (dekkingen) documents. "
                "Use this to find information about what is covered, "
                "exclusions, conditions, and insurance policy details. "
                "Input should be a search query in Dutch or English."
            )

        @tool(name=name, description=description)
        def search_tool(query: str) -> str:
            """Search insurance coverage documents."""
            results = self.retrieve(query, top_k=self.top_k)

            if not results:
                return "No relevant documents found."

            # Format results for the agent
            formatted = []
            for i, result in enumerate(results, 1):
                company = result.metadata.get('company', 'Unknown')
                doc_name = result.metadata.get('document_name', 'Unknown')
                formatted.append(
                    f"[Result {i}] (Score: {result.score:.2f}, Company: {company})\n"
                    f"{result.content}\n"
                )

            return "\n---\n".join(formatted)

        return search_tool

    def retrieve_by_metadata(
        self,
        company: Optional[str] = None,
        document_name: Optional[str] = None,
        header_1: Optional[str] = None,
        limit: int = 10,
    ) -> List[RetrievalResult]:
        """
        Retrieve documents by metadata filters without semantic search.

        Useful for browsing documents by company, document, or section.

        Args:
            company: Filter by company name
            document_name: Filter by document filename
            header_1: Filter by top-level header
            limit: Maximum number of results

        Returns:
            List of RetrievalResult objects
        """
        # Build filter conditions
        must_conditions = []

        if company:
            must_conditions.append(
                FieldCondition(
                    key="metadata.company",
                    match=MatchValue(value=company)
                )
            )

        if document_name:
            must_conditions.append(
                FieldCondition(
                    key="metadata.document_name",
                    match=MatchValue(value=document_name)
                )
            )

        if header_1:
            must_conditions.append(
                FieldCondition(
                    key="metadata.header_1",
                    match=MatchValue(value=header_1)
                )
            )

        if not must_conditions:
            raise ValueError("At least one metadata filter must be provided")

        # Use Qdrant scroll to get filtered results
        scroll_filter = Filter(must=must_conditions)

        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=scroll_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        # Convert to RetrievalResult objects
        retrieval_results = []
        for point in results:
            payload = point.payload if point.payload else {}
            retrieval_results.append(
                RetrievalResult(
                    content=payload.get("page_content", ""),
                    score=1.0,  # No similarity score for metadata-only search
                    metadata=payload.get("metadata", {}),
                )
            )

        return retrieval_results


def create_retriever(
    collection_name: str,
    method: RetrievalMethod = RetrievalMethod.SEMANTIC,
    top_k: int = DEFAULT_TOP_K,
    **kwargs
) -> DekkingenRetriever:
    """
    Factory function to create a configured retriever instance.

    Args:
        collection_name: Qdrant collection name (required)
        method: Retrieval method to use
        top_k: Number of results to return
        **kwargs: Additional configuration options

    Returns:
        Configured DekkingenRetriever instance
    """
    return DekkingenRetriever(collection_name=collection_name, method=method, top_k=top_k, **kwargs)


# Example usage
if __name__ == "__main__":
    # Example 1: Basic semantic search
    print("Example 1: Basic semantic search")
    print("=" * 60)

    retriever = create_retriever(
        collection_name=COLLECTION_NAME,
        method=RetrievalMethod.SEMANTIC,
        top_k=3
    )

    results = retriever.retrieve("What is covered by travel insurance?")

    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Score: {result.score:.3f}")
        print(f"Company: {result.metadata.get('company', 'N/A')}")
        print(f"Document: {result.metadata.get('document_name', 'N/A')}")
        print(f"Content preview: {result.content[:200]}...")

    # Example 2: Search with company filter
    print("\n\n" + "=" * 60)
    print("Example 2: Search with company filter")
    print("=" * 60)

    results = retriever.retrieve(
        "What are the exclusions for property damage?",
        company_filter="Goudse"
    )

    for i, result in enumerate(results, 1):
        print(f"\nResult {i}: {result}")

    # Example 3: Metadata-based retrieval
    print("\n\n" + "=" * 60)
    print("Example 3: Retrieve by metadata")
    print("=" * 60)

    results = retriever.retrieve_by_metadata(
        company="Henner",
        limit=5
    )

    print(f"Found {len(results)} documents from Henner")
    for result in results[:2]:
        print(f"\n{result}")
        print(f"Headers: {[k for k in result.metadata.keys() if k.startswith('header_')]}")
