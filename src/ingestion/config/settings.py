"""
Configuration settings for the ingestion pipeline.

This module contains all non-sensitive configuration settings.
Secrets and API keys should be stored in .env file.
"""

from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field
from qdrant_client.models import Distance


class EmbeddingSettings(BaseModel):
    """Embedding model configuration (non-sensitive)"""

    provider: Literal["openai", "gemini", "openrouter"] = "openai"
    model_name: str = "text-embedding-3-large"
    dimension: int = 3072
    batch_size: int = 100

    # OpenRouter specific
    openrouter_base_url: str = "https://openrouter.ai/api/v1"


class ChunkingSettings(BaseModel):
    """Text chunking configuration"""

    strategy: Literal["hierarchical", "hybrid"] = "hybrid"

    # Size-based settings
    max_chunk_size: int = 1000  # Maximum characters per chunk
    chunk_overlap: int = 100  # Overlap between chunks
    size_threshold: int = 800  # Split chunks larger than this

    # Hierarchical settings
    headers_to_split: list[tuple[str, str]] = Field(
        default=[
            ("#", "header_1"),
            ("##", "header_2"),
            ("###", "header_3"),
            ("####", "header_4"),
        ]
    )
    strip_headers: bool = False  # Keep headers in chunk content


class CollectionSettings(BaseModel):
    """Qdrant collection configuration"""

    name: str = "insurance_documents"
    distance_metric: Distance = Distance.COSINE

    # Hybrid retrieval (dense + sparse vectors)
    use_sparse: bool = True
    sparse_model: str = "Qdrant/bm25"
    dense_vector_name: str = "dense"
    sparse_vector_name: str = "sparse"


class IngestionSettings(BaseModel):
    """Main ingestion pipeline configuration"""

    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    chunking: ChunkingSettings = Field(default_factory=ChunkingSettings)
    collection: CollectionSettings = Field(default_factory=CollectionSettings)

    # Directories (relative to project root)
    documents_dir: str = "data/documents"
    chunks_output_dir: str = "data/documents/chunks"

    # Pipeline behavior
    enable_deduplication: bool = True
    save_chunks_to_disk: bool = True

    class Config:
        arbitrary_types_allowed = True


def load_settings(config_file: Optional[str] = None) -> IngestionSettings:
    """
    Load settings from YAML file or use defaults.

    Args:
        config_file: Path to YAML config file (optional)

    Returns:
        IngestionSettings instance
    """
    if config_file and Path(config_file).exists():
        try:
            import yaml
            with open(config_file) as f:
                data = yaml.safe_load(f)
            return IngestionSettings(**data)
        except Exception as e:
            print(f"Warning: Could not load config from {config_file}: {e}")
            print("Using default settings")

    return IngestionSettings()


# Default settings instance
DEFAULT_SETTINGS = IngestionSettings()
