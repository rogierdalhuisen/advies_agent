"""
Markdown document loader with metadata extraction.
"""

from pathlib import Path
from typing import List
from src.ingestion.loaders.base import DocumentLoader, Document
from src.ingestion.loaders.metadata_extractor import MetadataExtractor


class MarkdownLoader(DocumentLoader):
    """Load markdown files with metadata extraction"""

    def __init__(self, base_documents_dir: Path):
        """
        Initialize markdown loader.

        Args:
            base_documents_dir: Base directory for documents (e.g., data/documents)
        """
        self.base_documents_dir = base_documents_dir
        self.metadata_extractor = MetadataExtractor()

    def load(self, file_path: Path) -> Document:
        """
        Load a single markdown document.

        Args:
            file_path: Path to the markdown file

        Returns:
            Document instance with content and metadata
        """
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract metadata from path and filename
        metadata = self.metadata_extractor.extract_from_path(
            file_path, self.base_documents_dir
        )

        # Add content hash for change detection
        metadata["content_hash"] = self.metadata_extractor.compute_content_hash(content)

        return Document(content=content, metadata=metadata)

    def load_all(self, directory: Path = None) -> List[Document]:
        """
        Load all markdown documents from directory.

        Args:
            directory: Directory to load from (defaults to base_documents_dir)

        Returns:
            List of Document instances
        """
        if directory is None:
            directory = self.base_documents_dir

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        documents = []

        # Recursively find all .md files
        for md_file in directory.rglob("*.md"):
            try:
                doc = self.load(md_file)
                documents.append(doc)
            except Exception as e:
                print(f"Warning: Failed to load {md_file}: {e}")
                continue

        return documents

    def load_by_pattern(self, pattern: str) -> List[Document]:
        """
        Load markdown documents matching a glob pattern.

        Args:
            pattern: Glob pattern (e.g., "webpage_*.md", "goudse_*/conditions*.md")

        Returns:
            List of Document instances
        """
        documents = []

        for md_file in self.base_documents_dir.rglob(pattern):
            if md_file.is_file():
                try:
                    doc = self.load(md_file)
                    documents.append(doc)
                except Exception as e:
                    print(f"Warning: Failed to load {md_file}: {e}")
                    continue

        return documents

    def load_by_insurance(self, insurance_provider: str) -> List[Document]:
        """
        Load all documents for a specific insurance provider.

        Args:
            insurance_provider: Insurance provider folder name (e.g., "goudse_expat_pakket")

        Returns:
            List of Document instances
        """
        provider_dir = self.base_documents_dir / insurance_provider

        if not provider_dir.exists():
            raise FileNotFoundError(f"Insurance provider directory not found: {provider_dir}")

        return self.load_all(provider_dir)
