"""
Custom LangChain tools for retrieval with company-specific filtering.

This module provides factory functions to create LangChain tools that work
with a QdrantVectorStore instance for company-specific insurance coverage searches.
"""

from langchain.tools import tool
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import Filter, FieldCondition, MatchValue


def create_company_search_tool(vector_store: QdrantVectorStore):
    """
    Factory function to create a company-specific search tool.

    Args:
        vector_store: An initialized QdrantVectorStore instance

    Returns:
        A LangChain tool for searching company coverage
    """

    @tool
    def search_company_coverage(query: str, company: str, k: int = 5) -> list:
        """Search for insurance coverage information for a specific company.

        Use this tool to find what a specific insurance company covers for a given
        medical condition, treatment, or service. This will only return results
        from the specified company's coverage documents.

        Args:
            query: The search query describing the medical condition or treatment
            company: The insurance company name (e.g., 'Goudse', 'Henner')
            k: Maximum number of results to return (default: 5)

        Returns:
            A formatted string with search results including coverage details and metadata
        """
        # Create Qdrant filter for company metadata
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.company",
                    match=MatchValue(value=company)
                )
            ]
        )
        # Perform similarity search with company metadata filter
        results = vector_store.similarity_search_with_score(
            query,
            k=k,
            filter=qdrant_filter
        )

        return results

    return search_company_coverage


def create_company_hybrid_search_tool(vector_store: QdrantVectorStore):
    """
    Factory function to create a company-specific hybrid search tool.

    Args:
        vector_store: An initialized QdrantVectorStore instance with sparse embeddings

    Returns:
        A LangChain tool for hybrid searching company coverage
    """

    @tool
    def search_company_coverage_hybrid(query: str, company: str, k: int = 5) -> list:
        """Search for insurance coverage using hybrid search (dense + sparse) for a specific company.

        Use this tool when you need more comprehensive search results that combine
        semantic similarity (dense) with keyword matching (sparse). This will only
        return results from the specified company's coverage documents.

        Args:
            query: The search query describing the medical condition or treatment
            company: The insurance company name (e.g., 'Goudse', 'Henner')
            k: Maximum number of results to return (default: 5)

        Returns:
            A list of (Document, score) tuples with coverage details and metadata
        """
        # Create Qdrant filter for company metadata
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.company",
                    match=MatchValue(value=company)
                )
            ]
        )

        # Perform hybrid search with company metadata filter
        # Note: vector_store must be initialized with RetrievalMode.HYBRID
        # and have both dense and sparse embeddings configured
        results = vector_store.similarity_search_with_score(
            query,
            k=k,
            filter=qdrant_filter
        )

        return results

    return search_company_coverage_hybrid


def create_all_companies_dense_search_tool(vector_store: QdrantVectorStore):
    """
    Factory function to create a dense search tool across all companies.

    Args:
        vector_store: An initialized QdrantVectorStore instance

    Returns:
        A LangChain tool for searching across all companies
    """

    @tool
    def search_all_coverage_dense(query: str, k: int = 5) -> list:
        """Search for insurance coverage information across ALL insurance companies using dense search.

        Use this tool when you want to compare coverage across multiple insurance
        companies or when you don't know which company offers specific coverage.
        Uses semantic similarity search only.

        Args:
            query: The search query describing the medical condition or treatment
            k: Maximum number of results to return (default: 5)

        Returns:
            A list of (Document, score) tuples with coverage details and metadata from all companies
        """
        # Perform similarity search without any filter
        results = vector_store.similarity_search_with_score(
            query,
            k=k
        )

        return results

    return search_all_coverage_dense


def create_all_companies_hybrid_search_tool(vector_store: QdrantVectorStore):
    """
    Factory function to create a hybrid search tool across all companies.

    Args:
        vector_store: An initialized QdrantVectorStore instance with sparse embeddings

    Returns:
        A LangChain tool for hybrid searching across all companies
    """

    @tool
    def search_all_coverage_hybrid(query: str, k: int = 5) -> list:
        """Search for insurance coverage across ALL companies using hybrid search (dense + sparse).

        Use this tool when you want comprehensive search results across all insurance
        companies, combining semantic similarity with keyword matching.

        Args:
            query: The search query describing the medical condition or treatment
            k: Maximum number of results to return (default: 5)

        Returns:
            A list of (Document, score) tuples with coverage details and metadata from all companies
        """
        # Perform hybrid search without any filter
        # Note: vector_store must be initialized with RetrievalMode.HYBRID
        # and have both dense and sparse embeddings configured
        results = vector_store.similarity_search_with_score(
            query,
            k=k
        )

        return results

    return search_all_coverage_hybrid


