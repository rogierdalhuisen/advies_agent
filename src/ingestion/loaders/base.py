"""
Base classes for document loaders.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel


class Document(BaseModel):
    """Represents a loaded document with metadata"""

    content: str
    metadata: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True


class DocumentLoader(ABC):
    """Abstract base class for document loaders"""

    @abstractmethod
    def load(self, file_path: Path) -> Document:
        """
        Load a single document.

        Args:
            file_path: Path to the document file

        Returns:
            Document instance with content and metadata
        """
        pass

    @abstractmethod
    def load_all(self, directory: Path) -> List[Document]:
        """
        Load all documents from a directory.

        Args:
            directory: Path to directory containing documents

        Returns:
            List of Document instances
        """
        pass
