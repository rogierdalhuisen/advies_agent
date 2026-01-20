"""
Hybrid chunker: hierarchical (header-based) + size-based splitting.

First splits by markdown headers to preserve semantic structure,
then further splits large chunks to ensure manageable sizes.
"""

from typing import List, Dict, Any
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from src.ingestion.chunkers.base import Chunker, Chunk


class HybridChunker(Chunker):
    """
    Hierarchical + size-based chunking strategy.

    1. Split by markdown headers (preserve semantic structure)
    2. Further split large chunks by size (ensure manageable chunks)
    3. Maintain header context in sub-chunks
    """

    def __init__(
        self,
        headers_to_split: List[tuple[str, str]],
        max_chunk_size: int = 1000,
        chunk_overlap: int = 100,
        size_threshold: int = 800,
        strip_headers: bool = False
    ):
        """
        Initialize hybrid chunker.

        Args:
            headers_to_split: List of (header_mark, metadata_key) tuples
            max_chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between size-based chunks
            size_threshold: Split chunks larger than this
            strip_headers: Whether to remove headers from content
        """
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        self.size_threshold = size_threshold
        self.strip_headers = strip_headers

        # Hierarchical splitter
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split,
            strip_headers=strip_headers
        )

        # Size-based splitter for large chunks
        self.size_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

    def chunk(self, content: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split content using hybrid strategy.

        Args:
            content: Markdown text content
            metadata: Document metadata

        Returns:
            List of Chunk instances
        """
        # Step 1: Split by headers
        header_chunks = self.header_splitter.split_text(content)

        # Step 2: Check each chunk size and split if needed
        final_chunks = []
        global_chunk_index = 0

        for header_doc in header_chunks:
            chunk_text = header_doc.page_content
            chunk_metadata = {**metadata}

            # Add header hierarchy to metadata
            if header_doc.metadata:
                chunk_metadata.update(header_doc.metadata)

            # Check if chunk is too large
            if len(chunk_text) > self.size_threshold:
                # Split large chunk while preserving header context
                sub_chunks = self._split_large_chunk(
                    chunk_text,
                    chunk_metadata,
                    global_chunk_index
                )
                final_chunks.extend(sub_chunks)
                global_chunk_index += len(sub_chunks)
            else:
                # Keep chunk as is
                chunk = Chunk(
                    content=chunk_text,
                    metadata=chunk_metadata,
                    chunk_index=global_chunk_index
                )
                final_chunks.append(chunk)
                global_chunk_index += 1

        return final_chunks

    def _split_large_chunk(
        self,
        text: str,
        metadata: Dict[str, Any],
        start_index: int
    ) -> List[Chunk]:
        """
        Split a large chunk into smaller sub-chunks.

        Args:
            text: Chunk text to split
            metadata: Chunk metadata (includes header hierarchy)
            start_index: Starting chunk index

        Returns:
            List of sub-chunks
        """
        # Extract header context for prepending
        header_context = self._build_header_context(metadata)

        # Split into smaller pieces
        sub_texts = self.size_splitter.split_text(text)

        sub_chunks = []
        for idx, sub_text in enumerate(sub_texts):
            # Prepend header context to maintain semantic meaning
            if header_context:
                content_with_context = f"{header_context}\n\n{sub_text}"
            else:
                content_with_context = sub_text

            # Mark as sub-chunk in metadata
            sub_metadata = {
                **metadata,
                "is_sub_chunk": True,
                "sub_chunk_index": idx,
                "total_sub_chunks": len(sub_texts)
            }

            chunk = Chunk(
                content=content_with_context,
                metadata=sub_metadata,
                chunk_index=start_index + idx
            )
            sub_chunks.append(chunk)

        return sub_chunks

    def _build_header_context(self, metadata: Dict[str, Any]) -> str:
        """
        Build header context string from metadata.

        Args:
            metadata: Chunk metadata containing header hierarchy

        Returns:
            Formatted header string
        """
        headers = []

        # Extract headers in order (header_1, header_2, etc.)
        for i in range(1, 5):  # Support up to h4
            header_key = f"header_{i}"
            if header_key in metadata and metadata[header_key]:
                # Add appropriate number of # symbols
                headers.append(f"{'#' * i} {metadata[header_key]}")

        return "\n".join(headers)
