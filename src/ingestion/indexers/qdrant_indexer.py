"""
Qdrant vector store indexer with hybrid retrieval support.
"""

from typing import List, Dict, Any
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue, PointIdsList, SparseVectorParams

from src.ingestion.chunkers.base import Chunk
from src.ingestion.config.settings import CollectionSettings
from src.config import QDRANT_HOST


class QdrantIndexer:
    """
    Qdrant indexer with hybrid retrieval (dense + sparse) and deduplication.
    """

    def __init__(
        self,
        embeddings: Embeddings,
        collection_settings: CollectionSettings,
        embedding_dimension: int,
        enable_deduplication: bool = True
    ):
        """
        Initialize Qdrant indexer.

        Args:
            embeddings: Dense embeddings model
            collection_settings: Collection configuration
            embedding_dimension: Dimension of dense embeddings
            enable_deduplication: Whether to deduplicate before indexing
        """
        self.embeddings = embeddings
        self.collection_settings = collection_settings
        self.embedding_dimension = embedding_dimension
        self.enable_deduplication = enable_deduplication

        # Initialize Qdrant client
        self.client = QdrantClient(url=QDRANT_HOST)

        # Initialize sparse embeddings if hybrid mode enabled
        self.sparse_embeddings = None
        if collection_settings.use_sparse:
            self.sparse_embeddings = FastEmbedSparse(
                model_name=collection_settings.sparse_model
            )

    def initialize_collection(self) -> None:
        """
        Create Qdrant collection if it doesn't exist.

        Creates collection with dense and optionally sparse vectors.
        """
        collection_name = self.collection_settings.name

        # Check if collection exists
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if collection_name not in collection_names:
            print(f"Creating collection '{collection_name}'...")

            # Configure vectors
            if self.collection_settings.use_sparse:
                # Hybrid: dense + sparse vectors
                print(f"  → Hybrid retrieval enabled (dense + sparse)")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        self.collection_settings.dense_vector_name: VectorParams(
                            size=self.embedding_dimension,
                            distance=self.collection_settings.distance_metric
                        )
                    },
                    sparse_vectors_config={
                        self.collection_settings.sparse_vector_name: SparseVectorParams(
                            index=models.SparseIndexParams(on_disk=False)
                        )
                    },
                )
            else:
                # Dense only
                print(f"  → Dense vectors only")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=self.collection_settings.distance_metric
                    )
                )

            print(f"✅ Collection '{collection_name}' created successfully")
        else:
            print(f"✅ Collection '{collection_name}' already exists")

    def delete_by_document_id(self, document_id: str) -> int:
        """
        Delete all chunks for a specific document.

        Args:
            document_id: Document identifier to delete

        Returns:
            Number of points deleted
        """
        try:
            # Find all points with this document_id
            scroll_result = self.client.scroll(
                collection_name=self.collection_settings.name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                ),
                limit=10000,
                with_payload=False,
                with_vectors=False
            )

            point_ids = [point.id for point in scroll_result[0]]

            if point_ids:
                self.client.delete(
                    collection_name=self.collection_settings.name,
                    points_selector=PointIdsList(points=point_ids)
                )
                return len(point_ids)

            return 0

        except Exception as e:
            print(f"Warning: Failed to delete document {document_id}: {e}")
            return 0

    def deduplicate_documents(self, chunks: List[Chunk]) -> int:
        """
        Remove existing chunks for documents that will be re-indexed.

        Args:
            chunks: List of chunks to be indexed

        Returns:
            Number of chunks deleted
        """
        if not self.enable_deduplication:
            return 0

        print("\n🔄 Deduplicating existing documents...")

        # Get unique document IDs from chunks
        unique_doc_ids = set(
            chunk.metadata.get("document_id")
            for chunk in chunks
            if "document_id" in chunk.metadata
        )

        total_deleted = 0
        for doc_id in unique_doc_ids:
            deleted = self.delete_by_document_id(doc_id)
            if deleted > 0:
                print(f"  → Deleted {deleted} old chunks for document {doc_id[:8]}...")
            total_deleted += deleted

        if total_deleted > 0:
            print(f"✅ Deduplication complete: removed {total_deleted} old chunks")
        else:
            print("✅ No duplicates found")

        return total_deleted

    def index_chunks(self, chunks: List[Chunk]) -> QdrantVectorStore:
        """
        Index chunks into Qdrant with hybrid retrieval.

        Args:
            chunks: List of chunks to index

        Returns:
            QdrantVectorStore instance
        """
        # Ensure collection exists
        self.initialize_collection()

        # Deduplicate if enabled
        if self.enable_deduplication:
            self.deduplicate_documents(chunks)

        # Prepare texts and metadata
        texts = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        print(f"\n📥 Indexing {len(texts)} chunks into Qdrant...")

        # Create vector store and add documents
        if self.collection_settings.use_sparse:
            # Hybrid retrieval
            vector_store = QdrantVectorStore.from_texts(
                texts=texts,
                embedding=self.embeddings,
                sparse_embedding=self.sparse_embeddings,
                metadatas=metadatas,
                url=QDRANT_HOST,
                collection_name=self.collection_settings.name,
                retrieval_mode=RetrievalMode.HYBRID,
                vector_name=self.collection_settings.dense_vector_name,
                sparse_vector_name=self.collection_settings.sparse_vector_name,
                force_recreate=False
            )
            print(f"✅ Indexed {len(texts)} chunks with hybrid retrieval (dense + sparse)")
        else:
            # Dense only
            vector_store = QdrantVectorStore.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                url=QDRANT_HOST,
                collection_name=self.collection_settings.name,
                force_recreate=False
            )
            print(f"✅ Indexed {len(texts)} chunks with dense vectors")

        return vector_store

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            info = self.client.get_collection(self.collection_settings.name)
            return {
                "name": self.collection_settings.name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "status": info.status,
            }
        except Exception as e:
            return {"error": str(e)}
