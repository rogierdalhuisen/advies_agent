"""
Base classes for document chunking.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel


class Chunk(BaseModel):
    """Represents a text chunk with metadata"""

    content: str
    metadata: Dict[str, Any]
    chunk_index: int  # Position in document

    class Config:
        arbitrary_types_allowed = True


class Chunker(ABC):
    """Abstract base class for text chunkers"""

    @abstractmethod
    def chunk(self, content: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split text content into chunks.

        Args:
            content: Text content to chunk
            metadata: Document metadata to include in chunks

        Returns:
            List of Chunk instances
        """
        pass
