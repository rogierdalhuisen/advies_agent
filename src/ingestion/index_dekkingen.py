"""
Ingestion script for processing and indexing insurance coverage (dekkingen) documents.

This script uses hierarchical chunking to split markdown documents by headers,
preserves metadata including headers, document name, company, and timestamp,
and stores embeddings in Qdrant vector database using LangChain framework.

The design is modular - swap embedding models or vector stores by changing
configuration constants at the top of the file.

Usage:
    python -m src.ingestion.index_dekkingen
    or
    uv run python -m src.ingestion.index_dekkingen
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from pydantic import SecretStr
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from src.config import DOCUMENTS_DIR, QDRANT_HOST, GEMINI_API_KEY


# ==================== CONFIGURATION ====================
# Change these constants to swap models or adjust behavior

COLLECTION_NAME = "dekkingen"
EMBEDDING_MODEL_NAME = "models/embedding-001"  # Google's embedding model
EMBEDDING_DIMENSION = 768  # embedding-001 produces 768-dimensional vectors
DISTANCE_METRIC = Distance.COSINE

# Headers to split on (hierarchical levels)
HEADERS_TO_SPLIT = [
    ("#", "header_1"),
    ("##", "header_2"),
    ("###", "header_3"),
    ("####", "header_4"),
    ("#####", "header_5"),
]

# Directory containing dekkingen markdown files
DEKKINGEN_DIR = DOCUMENTS_DIR / "dekkingen"
CHUNKS_OUTPUT_DIR = DEKKINGEN_DIR / "chunks"

# =======================================================


def extract_company_from_filename(filename: str) -> str:
    """
    Extract company name from filename.

    Example: 'goudse_dekking.md' -> 'Goudse'
    """
    base_name = filename.replace("_dekking.md", "").replace("_", " ")
    return base_name.title()


def load_markdown_documents(directory: Path) -> List[Dict[str, Any]]:
    """
    Load all markdown files from the specified directory.

    Args:
        directory: Path to directory containing markdown files

    Returns:
        List of dictionaries containing file metadata and content
    """
    documents = []

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    for file_path in directory.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        documents.append({
            "content": content,
            "filename": file_path.name,
            "filepath": str(file_path),
            "company": extract_company_from_filename(file_path.name),
            "ingestion_timestamp": datetime.now().isoformat(),
        })

    return documents


def create_hierarchical_chunks(
    documents: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Split documents using hierarchical markdown header chunking.

    Args:
        documents: List of document dictionaries with content and metadata

    Returns:
        List of chunks with preserved header hierarchy and metadata
    """
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT,
        strip_headers=False  # Keep headers in the chunk content
    )

    all_chunks = []

    for doc in documents:
        # Split the document by headers
        splits = splitter.split_text(doc["content"])

        # Enrich each chunk with document-level metadata
        for chunk in splits:
            chunk_dict = {
                "content": chunk.page_content,
                "document_name": doc["filename"],
                "company": doc["company"],
                "ingestion_timestamp": doc["ingestion_timestamp"],
                "filepath": doc["filepath"],
            }

            # Add header hierarchy as metadata
            if chunk.metadata:
                chunk_dict.update(chunk.metadata)

            all_chunks.append(chunk_dict)

    return all_chunks


def save_chunks_to_disk(chunks: List[Dict[str, Any]], output_dir: Path) -> None:
    """
    Save document chunks to disk for inspection.

    Args:
        chunks: List of document chunks with metadata
        output_dir: Directory to save chunk files
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing chunk files
    for existing_file in output_dir.glob("*.txt"):
        existing_file.unlink()

    print(f"Saving {len(chunks)} chunks to {output_dir}...")

    for idx, chunk in enumerate(chunks):
        # Create a readable filename with company and chunk number
        company = chunk.get("company", "unknown")
        filename = f"{company.lower().replace(' ', '_')}_chunk_{idx:04d}.txt"
        filepath = output_dir / filename

        # Write chunk content and metadata
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"CHUNK {idx + 1} of {len(chunks)}\n")
            f.write("=" * 80 + "\n\n")

            # Write metadata
            f.write("METADATA:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Company: {chunk.get('company', 'N/A')}\n")
            f.write(f"Document: {chunk.get('document_name', 'N/A')}\n")
            f.write(f"Filepath: {chunk.get('filepath', 'N/A')}\n")
            f.write(f"Ingestion Timestamp: {chunk.get('ingestion_timestamp', 'N/A')}\n")

            # Write header hierarchy
            headers = {k: v for k, v in chunk.items() if k.startswith("header_")}
            if headers:
                f.write("\nHeader Hierarchy:\n")
                for header_key in sorted(headers.keys()):
                    f.write(f"  {header_key}: {headers[header_key]}\n")

            f.write("\n" + "=" * 80 + "\n\n")

            # Write actual chunk content
            f.write("CONTENT:\n")
            f.write("-" * 40 + "\n")
            f.write(chunk.get("content", ""))
            f.write("\n")

    print(f"Saved {len(chunks)} chunks successfully.")


def initialize_qdrant_collection(client: QdrantClient, collection_name: str) -> None:
    """
    Initialize Qdrant collection if it doesn't exist.

    Args:
        client: QdrantClient instance
        collection_name: Name of the collection to create
    """
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]

    if collection_name not in collection_names:
        print(f"Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=DISTANCE_METRIC
            ),
        )
        print(f"Collection '{collection_name}' created successfully.")
    else:
        print(f"Collection '{collection_name}' already exists.")


def index_chunks_to_qdrant(chunks: List[Dict[str, Any]]) -> QdrantVectorStore:
    """
    Index document chunks into Qdrant vector store.

    Args:
        chunks: List of document chunks with metadata

    Returns:
        QdrantVectorStore instance
    """
    # Initialize embedding model
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=SecretStr(GEMINI_API_KEY) if GEMINI_API_KEY else None
    )

    # Initialize Qdrant client
    client = QdrantClient(url=QDRANT_HOST)

    # Ensure collection exists
    initialize_qdrant_collection(client, COLLECTION_NAME)

    # Prepare texts and metadata for indexing
    texts = [chunk["content"] for chunk in chunks]
    metadatas = [
        {
            "document_name": chunk["document_name"],
            "company": chunk["company"],
            "ingestion_timestamp": chunk["ingestion_timestamp"],
            "filepath": chunk["filepath"],
            **{k: v for k, v in chunk.items()
               if k.startswith("header_")}  # Include all header levels
        }
        for chunk in chunks
    ]

    # Create vector store and add documents
    print(f"Indexing {len(texts)} chunks into Qdrant...")
    vector_store = QdrantVectorStore.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        url=QDRANT_HOST,
        collection_name=COLLECTION_NAME,
        force_recreate=False  # Don't recreate if collection exists
    )

    print(f"Successfully indexed {len(texts)} chunks.")
    return vector_store


def main():
    """
    Main execution function for the ingestion pipeline.
    """
    print("=" * 60)
    print("Starting Dekkingen Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Load markdown documents
    print(f"\n[1/3] Loading documents from {DEKKINGEN_DIR}...")
    documents = load_markdown_documents(DEKKINGEN_DIR)
    print(f"Loaded {len(documents)} documents.")

    # Step 2: Create hierarchical chunks
    print("\n[2/4] Creating hierarchical chunks...")
    chunks = create_hierarchical_chunks(documents)
    print(f"Created {len(chunks)} chunks with header hierarchy.")

    # Step 3: Save chunks to disk for inspection
    print(f"\n[3/4] Saving chunks to {CHUNKS_OUTPUT_DIR}...")
    save_chunks_to_disk(chunks, CHUNKS_OUTPUT_DIR)

    # Step 4: Index to Qdrant
    print("\n[4/4] Indexing chunks to Qdrant...")
    index_chunks_to_qdrant(chunks)

    print("\n" + "=" * 60)
    print("Ingestion Pipeline Completed Successfully!")
    print("=" * 60)
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Total chunks indexed: {len(chunks)}")
    print(f"Embedding model: {EMBEDDING_MODEL_NAME}")
    print(f"Qdrant host: {QDRANT_HOST}")


if __name__ == "__main__":
    main()
