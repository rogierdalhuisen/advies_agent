"""
Hierarchical chunker based on markdown headers.
"""

from typing import List, Dict, Any
from langchain_text_splitters import MarkdownHeaderTextSplitter
from src.ingestion.chunkers.base import Chunker, Chunk


class HierarchicalChunker(Chunker):
    """Split documents by markdown header hierarchy"""

    def __init__(
        self,
        headers_to_split: List[tuple[str, str]],
        strip_headers: bool = False
    ):
        """
        Initialize hierarchical chunker.

        Args:
            headers_to_split: List of (header_mark, metadata_key) tuples
                              e.g., [("#", "h1"), ("##", "h2")]
            strip_headers: Whether to remove headers from chunk content
        """
        self.headers_to_split = headers_to_split
        self.strip_headers = strip_headers
        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split,
            strip_headers=strip_headers
        )

    def chunk(self, content: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split content by markdown headers.

        Args:
            content: Markdown text content
            metadata: Document metadata

        Returns:
            List of Chunk instances with header hierarchy in metadata
        """
        # Split by headers
        langchain_docs = self.splitter.split_text(content)

        chunks = []
        for idx, doc in enumerate(langchain_docs):
            # Combine document metadata with header metadata
            chunk_metadata = {**metadata}

            # Add header hierarchy from LangChain document
            if doc.metadata:
                chunk_metadata.update(doc.metadata)

            # Create chunk
            chunk = Chunk(
                content=doc.page_content,
                metadata=chunk_metadata,
                chunk_index=idx
            )
            chunks.append(chunk)

        return chunks
