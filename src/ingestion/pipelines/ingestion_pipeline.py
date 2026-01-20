"""
Main ingestion pipeline orchestrating the complete flow.

Coordinates: loading → chunking → embedding → indexing
"""

from pathlib import Path
from typing import List, Optional
from src.ingestion.config.settings import IngestionSettings, load_settings
from src.ingestion.loaders.markdown_loader import MarkdownLoader
from src.ingestion.chunkers.base import Chunk
from src.ingestion.chunkers.hierarchical import HierarchicalChunker
from src.ingestion.chunkers.hybrid import HybridChunker
from src.ingestion.embedders.factory import EmbedderFactory
from src.ingestion.indexers.qdrant_indexer import QdrantIndexer


class IngestionPipeline:
    """
    Orchestrates the complete ingestion pipeline.
    """

    def __init__(self, settings: IngestionSettings = None, config_file: str = None):
        """
        Initialize ingestion pipeline.

        Args:
            settings: IngestionSettings instance (optional, uses defaults if not provided)
            config_file: Path to YAML config file (optional)
        """
        # Load settings
        if settings is None:
            settings = load_settings(config_file)

        self.settings = settings

        # Initialize components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize pipeline components"""

        # Document loader
        documents_dir = Path(self.settings.documents_dir)
        self.loader = MarkdownLoader(base_documents_dir=documents_dir)

        # Chunker (hierarchical or hybrid)
        if self.settings.chunking.strategy == "hierarchical":
            self.chunker = HierarchicalChunker(
                headers_to_split=self.settings.chunking.headers_to_split,
                strip_headers=self.settings.chunking.strip_headers
            )
        else:  # hybrid
            self.chunker = HybridChunker(
                headers_to_split=self.settings.chunking.headers_to_split,
                max_chunk_size=self.settings.chunking.max_chunk_size,
                chunk_overlap=self.settings.chunking.chunk_overlap,
                size_threshold=self.settings.chunking.size_threshold,
                strip_headers=self.settings.chunking.strip_headers
            )

        # Embedder
        self.embeddings = EmbedderFactory.create(self.settings.embedding)
        embedding_dim = EmbedderFactory.get_embedding_dimension(self.settings.embedding)

        # Indexer
        self.indexer = QdrantIndexer(
            embeddings=self.embeddings,
            collection_settings=self.settings.collection,
            embedding_dimension=embedding_dim,
            enable_deduplication=self.settings.enable_deduplication
        )

    def run(
        self,
        document_pattern: Optional[str] = None,
        insurance_provider: Optional[str] = None
    ) -> dict:
        """
        Run the complete ingestion pipeline.

        Args:
            document_pattern: Optional glob pattern to filter documents (e.g., "webpage_*.md")
            insurance_provider: Optional insurance provider folder name to filter

        Returns:
            Dictionary with pipeline statistics
        """
        print("=" * 60)
        print("Starting Ingestion Pipeline")
        print("=" * 60)
        print(f"Embedding: {self.settings.embedding.provider}/{self.settings.embedding.model_name}")
        print(f"Chunking: {self.settings.chunking.strategy}")
        print(f"Collection: {self.settings.collection.name}")
        print(f"Deduplication: {'enabled' if self.settings.enable_deduplication else 'disabled'}")
        print("=" * 60)

        # Step 1: Load documents
        print("\n[1/4] Loading documents...")
        if insurance_provider:
            documents = self.loader.load_by_insurance(insurance_provider)
            print(f"✅ Loaded {len(documents)} documents for {insurance_provider}")
        elif document_pattern:
            documents = self.loader.load_by_pattern(document_pattern)
            print(f"✅ Loaded {len(documents)} documents matching '{document_pattern}'")
        else:
            documents = self.loader.load_all()
            print(f"✅ Loaded {len(documents)} documents")

        if not documents:
            print("❌ No documents found!")
            return {"error": "No documents found"}

        # Step 2: Chunk documents
        print("\n[2/4] Chunking documents...")
        all_chunks: List[Chunk] = []

        for doc in documents:
            chunks = self.chunker.chunk(doc.content, doc.metadata)
            all_chunks.extend(chunks)

        print(f"✅ Created {len(all_chunks)} chunks")

        # Step 3: Save chunks to disk (optional)
        if self.settings.save_chunks_to_disk:
            print("\n[3/4] Saving chunks to disk...")
            self._save_chunks_to_disk(all_chunks)
        else:
            print("\n[3/4] Skipping chunk disk save")

        # Step 4: Index to Qdrant
        print("\n[4/4] Indexing to Qdrant...")
        vector_store = self.indexer.index_chunks(all_chunks)

        # Get collection info
        collection_info = self.indexer.get_collection_info()

        print("\n" + "=" * 60)
        print("✅ Ingestion Pipeline Completed Successfully!")
        print("=" * 60)
        print(f"Documents processed: {len(documents)}")
        print(f"Chunks indexed: {len(all_chunks)}")
        print(f"Collection: {self.settings.collection.name}")
        print(f"Total points in collection: {collection_info.get('points_count', 'unknown')}")
        print("=" * 60)

        return {
            "documents_processed": len(documents),
            "chunks_created": len(all_chunks),
            "collection_name": self.settings.collection.name,
            "collection_info": collection_info
        }

    def _save_chunks_to_disk(self, chunks: List[Chunk]):
        """
        Save chunks to disk for inspection.

        Args:
            chunks: List of chunks to save
        """
        output_dir = Path(self.settings.chunks_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Clear existing files
        for existing_dir in output_dir.iterdir():
            if existing_dir.is_dir():
                for existing_file in existing_dir.glob("*.txt"):
                    existing_file.unlink()

        print(f"  → Saving {len(chunks)} chunks to {output_dir}...")

        # Group by insurance provider
        company_counts = {}

        for idx, chunk in enumerate(chunks):
            # Get insurance provider
            insurance = chunk.metadata.get("insurance_provider", "unknown")
            company_dir = output_dir / insurance.lower().replace(" ", "_")
            company_dir.mkdir(parents=True, exist_ok=True)

            # Track chunk number per company
            if insurance not in company_counts:
                company_counts[insurance] = 0
            company_counts[insurance] += 1
            chunk_num = company_counts[insurance]

            # Create filename
            filename = f"chunk_{chunk_num:04d}.txt"
            filepath = company_dir / filename

            # Write chunk
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write(f"CHUNK {chunk_num} (Global: {idx + 1}/{len(chunks)})\n")
                f.write("=" * 80 + "\n\n")

                # Metadata
                f.write("METADATA:\n")
                f.write("-" * 40 + "\n")
                for key, value in chunk.metadata.items():
                    f.write(f"{key}: {value}\n")

                f.write("\n" + "=" * 80 + "\n\n")

                # Content
                f.write("CONTENT:\n")
                f.write("-" * 40 + "\n")
                f.write(chunk.content)
                f.write("\n")

        print(f"  ✅ Saved {len(chunks)} chunks to {len(company_counts)} company folders")
