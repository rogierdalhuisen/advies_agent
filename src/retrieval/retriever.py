"""Retriever module for hybrid search over insurance documents."""

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from config import (
    EMBEDDING_MODEL,
    SPARSE_EMBEDDING_MODEL,
    COLLECTION_NAME,
    DENSE_VECTOR_NAME,
    SPARSE_VECTOR_NAME,
    QDRANT_URL,
    OPENAI_KEY,
)


class InsuranceRetriever:
    """Hybrid retriever for insurance documents with company filtering."""

    def __init__(
        self,
        qdrant_url: str = QDRANT_URL,
        collection_name: str = COLLECTION_NAME,
        embedding_model: str = EMBEDDING_MODEL,
        sparse_model: str = SPARSE_EMBEDDING_MODEL,
        openai_api_key: str = OPENAI_KEY,
    ):
        """Initialize the retriever with embeddings and vector store.

        Args:
            qdrant_url: URL of the Qdrant instance.
            collection_name: Name of the Qdrant collection.
            embedding_model: OpenAI embedding model name.
            sparse_model: Sparse embedding model name.
            openai_api_key: OpenAI API key.
        """
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            api_key=openai_api_key,
        )
        self.sparse_embeddings = FastEmbedSparse(model_name=sparse_model)
        self.client = QdrantClient(url=qdrant_url)

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.embeddings,
            sparse_embedding=self.sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name=DENSE_VECTOR_NAME,
            sparse_vector_name=SPARSE_VECTOR_NAME,
        )

    def retrieve_company_docs(
        self, query: str, insurance_provider: str, k: int = 5
    ) -> list:
        """Search for documents matching a query filtered by insurance company.

        Args:
            query: The search query.
            insurance_provider: The insurance provider name to filter by.
            k: Number of results to return.

        Returns:
            List of (Document, score) tuples.
        """
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.insurance_provider",
                    match=MatchValue(value=insurance_provider),
                )
            ]
        )

        results = self.vector_store.similarity_search_with_score(
            query,
            k=k,
            filter=qdrant_filter,
        )

        return results

    def retrieve_docs(self, query: str, k: int = 5) -> list:
        """Search for documents matching a query without filtering.

        Args:
            query: The search query.
            k: Number of results to return.

        Returns:
            List of (Document, score) tuples.
        """
        return self.vector_store.similarity_search_with_score(query, k=k)
    
    
    def format_document_with_context(self, doc) -> str:
        """Restores headers from metadata into the text content."""
        
        # Extract headers from metadata (keys depend on your Splitter setup)
        # MarkdownHeaderTextSplitter usually keys them as "Header 1", "Header 2", etc.
        headers = [
            doc.metadata.get(key) 
            for key in ["Header 1", "Header 2", "Header 3"] 
            if doc.metadata.get(key)
        ]
        
        # Create a context string (e.g., "Policy > Auto > Coverage A")
        context_path = " > ".join(headers)
        
        # Return formatted string
        if context_path:
            return f"Context: {context_path}\nContent: {doc.page_content}"
        return doc.page_content


# Default retriever instance for convenience
retriever = InsuranceRetriever()

#  Usage:                                                                                                                                        
#   from src.retrieval.retriever import InsuranceRetriever, retriever                                                                             
                                                                                                                                                
#   # Use default instance                                                                                                                        
#   results = retriever.search_company_coverage_hybrid("water damage", "Allianz", k=10)                                                           
                                                                                                                                                
#   # Or create custom instance                                                                                                                   
#   custom_retriever = InsuranceRetriever(collection_name="other_collection")  
