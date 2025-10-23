"""
Ingestion script for processing and indexing insurance coverage (dekkingen) documents.

This script uses hierarchical chunking to split markdown documents by headers,
preserves metadata including headers, document name, company, and timestamp,
and stores embeddings in Qdrant vector database using LangChain framework.

DEDUPLICATION STRATEGY:
- Uses filepath as unique document identifier
- Before indexing: deletes all existing chunks for that document
- Then: indexes fresh chunks (Strategy A: Replace)

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
import hashlib

from pydantic import SecretStr
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue, PointIdsList

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


def generate_document_id(filepath: str) -> str:
    """
    Generate a unique, stable document ID from filepath.

    Uses SHA-256 hash truncated to 16 characters for uniqueness.

    Args:
        filepath: Full path to the document

    Returns:
        Unique document identifier
    """
    return hashlib.sha256(filepath.encode()).hexdigest()[:16]


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

        filepath_str = str(file_path)
        documents.append({
            "content": content,
            "filename": file_path.name,
            "filepath": filepath_str,
            "document_id": generate_document_id(filepath_str),
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
                "document_id": doc["document_id"],
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
    Save document chunks to disk for inspection, organized by company.

    Args:
        chunks: List of document chunks with metadata
        output_dir: Directory to save chunk files
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing company subdirectories and chunk files
    for existing_dir in output_dir.iterdir():
        if existing_dir.is_dir():
            for existing_file in existing_dir.glob("*.txt"):
                existing_file.unlink()
            existing_dir.rmdir()

    print(f"Saving {len(chunks)} chunks to {output_dir}...")

    # Group chunks by company for numbering
    company_chunk_counts = {}

    for idx, chunk in enumerate(chunks):
        # Get company name and create company-specific subdirectory
        company = chunk.get("company", "unknown")
        company_dir = output_dir / company.lower().replace(' ', '_')
        company_dir.mkdir(parents=True, exist_ok=True)

        # Track chunk number per company
        if company not in company_chunk_counts:
            company_chunk_counts[company] = 0
        company_chunk_counts[company] += 1
        chunk_num = company_chunk_counts[company]

        # Create filename with company-specific chunk number
        filename = f"chunk_{chunk_num:04d}.txt"
        filepath = company_dir / filename

        # Write chunk content and metadata
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"CHUNK {chunk_num} (Global: {idx + 1} of {len(chunks)})\n")
            f.write("=" * 80 + "\n\n")

            # Write metadata
            f.write("METADATA:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Company: {chunk.get('company', 'N/A')}\n")
            f.write(f"Document: {chunk.get('document_name', 'N/A')}\n")
            f.write(f"Document ID: {chunk.get('document_id', 'N/A')}\n")
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
    print(f"Organized into {len(company_chunk_counts)} company folders: {', '.join(company_chunk_counts.keys())}")


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


def delete_document_from_qdrant(
    client: QdrantClient,
    collection_name: str,
    document_id: str
) -> int:
    """
    Delete all chunks belonging to a specific document from Qdrant.

    Args:
        client: QdrantClient instance
        collection_name: Name of the collection
        document_id: Unique document identifier

    Returns:
        Number of points deleted
    """
    try:
        # Scroll through all points to find matching document_id
        scroll_result = client.scroll(
            collection_name=collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            ),
            limit=1000,  # Adjust if documents have more chunks
            with_payload=False,
            with_vectors=False
        )

        point_ids = [point.id for point in scroll_result[0]]

        if point_ids:
            client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=point_ids)
            )
            print(f"  → Deleted {len(point_ids)} existing chunks for document_id: {document_id}")
            return len(point_ids)
        else:
            print(f"  → No existing chunks found for document_id: {document_id}")
            return 0

    except Exception as e:
        print(f"  ⚠ Warning: Could not delete existing chunks: {e}")
        return 0


def index_chunks_to_qdrant(chunks: List[Dict[str, Any]]) -> QdrantVectorStore:
    """
    Index document chunks into Qdrant vector store with deduplication.

    DEDUPLICATION: Before indexing, deletes all existing chunks for each document
    based on document_id (Strategy A: Replace).

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

    # === DEDUPLICATION: Delete existing documents before re-indexing ===
    print("\n🔄 Checking for existing documents to deduplicate...")
    unique_document_ids = set(chunk["document_id"] for chunk in chunks)

    total_deleted = 0
    for doc_id in unique_document_ids:
        deleted_count = delete_document_from_qdrant(client, COLLECTION_NAME, doc_id)
        total_deleted += deleted_count

    if total_deleted > 0:
        print(f"✅ Deduplication complete: removed {total_deleted} old chunks")
    else:
        print("✅ No duplicates found, proceeding with fresh indexing")

    # Prepare texts and metadata for indexing
    texts = [chunk["content"] for chunk in chunks]
    metadatas = [
        {
            "document_name": chunk["document_name"],
            "document_id": chunk["document_id"],
            "company": chunk["company"],
            "ingestion_timestamp": chunk["ingestion_timestamp"],
            "filepath": chunk["filepath"],
            **{k: v for k, v in chunk.items()
               if k.startswith("header_")}  # Include all header levels
        }
        for chunk in chunks
    ]

    # Create vector store and add documents
    print(f"\n📥 Indexing {len(texts)} chunks into Qdrant...")
    vector_store = QdrantVectorStore.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        url=QDRANT_HOST,
        collection_name=COLLECTION_NAME,
        force_recreate=False  # Don't recreate if collection exists
    )

    print(f"✅ Successfully indexed {len(texts)} chunks.")
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
