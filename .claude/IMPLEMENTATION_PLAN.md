# Implementation Plan: RAG-Based Insurance Advice Agent

> _This is an example implementation plan for building a complete RAG (Retrieval-Augmented Generation) system for Dutch expat insurance advice using LangGraph and Qdrant._

## 1 Overview

Build an AI agent that provides accurate insurance advice by retrieving relevant information from insurance policy documents (Goudse, Henner) and generating contextual answers. The system uses LangGraph for orchestration, Qdrant for vector storage, and LangChain for document processing and retrieval.

## 2 Current State Analysis

### 2.1 Existing System

Currently, the project has:

1. **Configuration** – Basic project setup with Qdrant connection config in `src/config.py`
2. **Documents** – Insurance policy documents in markdown format under `data/documents/dekkingen/` about coverages, premiums will be under `data/documents/premies/` en voorwaardes onder `data/documents/voorwaardes/`, they will be handles differently
3. **Infrastructure** – Docker Compose setup with agent, Qdrant, and Jupyter services
4. **Dependencies** – Core dependencies: langchain-qdrant, qdrant-client

### 2.2 Current Data Model

The insurance documents contain structured information about:

- **Policy Coverage** – Different coverage packages (Standaard, Optimaal, Excellent)
- **Benefits** – Specific benefits per package (SOS assistance, medical coverage, pregnancy/childbirth)
- **Pricing** – Premium tables based on family composition and region
- **Conditions** – Coverage limits, deductibles, waiting periods

### 2.3 Proposed Architecture

```
User Query → LangGraph Agent → [
  1. Query Analyzer (understand intent)
  2. Vector Retrieval (Qdrant search)
  3. Reranking (select best chunks)
  4. Answer Generator (LLM with context)
  5. Source Citation (add references)
] → Response with Sources
```

---

## 3 Implementation Progress Tracker

| Step | Area / Component                         | Status | Dependencies | Ready to Close? |
| ---- | ---------------------------------------- | ------ | ------------ | --------------- |
| 1.1  | Project structure: Create module folders | ☐      | —            | ☐               |
| 1.2  | Models: Define data models               | ☐      | 1.1          | ☐               |
| 2.1  | Ingestion: Document loader & chunking    | ☐      | 1.x          | ☐               |
| 2.2  | Ingestion: Embeddings & Qdrant upload    | ☐      | 2.1          | ☐               |
| 2.3  | Ingestion: CLI tool for data loading     | ☐      | 2.2          | ☐               |
| 3.1  | Retrieval: Qdrant client wrapper         | ☐      | 1.2, 2.2     | ☐               |
| 3.2  | Retrieval: Query expansion               | ☐      | 3.1          | ☐               |
| 3.3  | Retrieval: Reranking logic               | ☐      | 3.1          | ☐               |
| 4.1  | Graph: LangGraph state definition        | ☐      | 1.2          | ☐               |
| 4.2  | Graph: Query analyzer node               | ☐      | 4.1          | ☐               |
| 4.3  | Graph: Retrieval node                    | ☐      | 3.x, 4.1     | ☐               |
| 4.4  | Graph: Answer generation node            | ☐      | 4.1, 4.3     | ☐               |
| 4.5  | Graph: Source citation node              | ☐      | 4.4          | ☐               |
| 4.6  | Graph: Compile complete workflow         | ☐      | 4.x          | ☐               |
| 5.1  | Interface: CLI interface                 | ☐      | 4.6          | ☐               |
| 5.2  | Interface: Evaluation notebook           | ☐      | 4.6          | ☐               |
| 6.1  | Testing: Unit tests for components       | ☐      | All          | ☐               |
| 6.2  | Testing: Integration tests               | ☐      | All          | ☐               |
| 6.3  | Testing: Evaluation metrics              | ☐      | 5.2          | ☐               |

---

## 4 Implementation Plan

### Step 1.1: Project Structure

**Purpose / Scope**

Create a clean module structure for the agent codebase following Python best practices.

**Requirements**

- Separate modules for ingestion, retrieval, graph, and models
- Clear separation of concerns
- Easy to navigate and extend

**Implementation**

```
src/
├── __init__.py
├── config.py                    # Already exists
├── main.py                      # Entry point
├── models/
│   ├── __init__.py
│   └── schemas.py              # Pydantic models for requests/responses
├── ingestion/
│   ├── __init__.py
│   ├── loader.py               # Document loading
│   ├── chunker.py              # Text splitting strategies
│   └── embedder.py             # Embedding creation
├── retrieval/
│   ├── __init__.py
│   ├── qdrant_client.py        # Qdrant operations
│   ├── query_expansion.py      # Query rewriting
│   └── reranker.py             # Reranking logic
├── graph/
│   ├── __init__.py
│   ├── state.py                # LangGraph state definition
│   ├── nodes.py                # Individual nodes
│   └── workflow.py             # Complete graph assembly
├── utils/
│   ├── __init__.py
│   └── logging.py              # Logging utilities
└── cli.py                       # CLI interface
```

**Acceptance Criteria**

- All modules created with proper `__init__.py`
- No circular import issues
- Imports work correctly from main.py

**Testing Strategy**

- Unit test: Import all modules without errors
- Unit test: Verify package structure with `pkg_resources`

---

### Step 1.2: Data Models

**Purpose / Scope**

Define Pydantic models for type safety and validation throughout the application.

**Requirements**

- Models for documents, chunks, queries, and responses
- Proper validation and serialization
- Include metadata structures

**Implementation**

<details markdown="1">
<summary markdown="span">src/models/schemas.py</summary>

```python
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata for insurance documents."""
    source_file: str
    insurance_provider: str  # e.g., "Goudse", "Henner"
    document_type: str  # e.g., "coverage", "premiums", "conditions"
    plan_level: Optional[str] = None  # e.g., "Standaard", "Optimaal", "Excellent"
    last_updated: datetime = Field(default_factory=datetime.now)


class DocumentChunk(BaseModel):
    """A chunk of text from a document."""
    chunk_id: str
    text: str
    metadata: DocumentMetadata
    embedding: Optional[List[float]] = None

    class Config:
        arbitrary_types_allowed = True


class Query(BaseModel):
    """User query."""
    text: str
    user_context: Optional[Dict[str, Any]] = None  # e.g., family_size, region


class RetrievedChunk(BaseModel):
    """Retrieved chunk with score."""
    chunk: DocumentChunk
    score: float
    rank: Optional[int] = None


class Answer(BaseModel):
    """Generated answer with sources."""
    answer_text: str
    sources: List[RetrievedChunk]
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """State for LangGraph workflow."""
    original_query: Query
    expanded_queries: Optional[List[str]] = None
    retrieved_chunks: List[RetrievedChunk] = Field(default_factory=list)
    reranked_chunks: List[RetrievedChunk] = Field(default_factory=list)
    answer: Optional[Answer] = None

    class Config:
        arbitrary_types_allowed = True
```

</details>

**Acceptance Criteria**

- All models have proper type hints
- Models can be serialized to/from JSON
- Validation works for required fields

**Testing Strategy**

- Unit tests: Test model validation with valid/invalid data
- Unit tests: Test serialization/deserialization

---

### Step 2.1: Document Loading & Chunking

**Purpose / Scope**

Load markdown insurance documents and split them into semantic chunks suitable for retrieval.

**Requirements**

- Load all markdown files from `data/documents/`
- Preserve document structure (headings, sections)
- Smart chunking that keeps related content together
- Extract metadata from file paths and content

**Implementation**

<details markdown="1">
<summary markdown="span">src/ingestion/loader.py</summary>

```python
from pathlib import Path
from typing import List
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from src.models.schemas import DocumentMetadata
from src.config import DOCUMENTS_DIR


class InsuranceDocumentLoader:
    """Load insurance documents from markdown files."""

    def __init__(self, documents_dir: Path = DOCUMENTS_DIR):
        self.documents_dir = documents_dir

    def load_all(self) -> List[tuple[str, DocumentMetadata]]:
        """
        Load all markdown documents.

        Returns:
            List of (content, metadata) tuples
        """
        documents = []

        for md_file in self.documents_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            metadata = self._extract_metadata(md_file)
            documents.append((content, metadata))

        return documents

    def _extract_metadata(self, file_path: Path) -> DocumentMetadata:
        """Extract metadata from file path and content."""
        # Parse provider from filename (e.g., "goudse_dekking.md" -> "Goudse")
        provider = file_path.stem.split("_")[0].capitalize()

        # Determine document type from parent directory
        doc_type = file_path.parent.name

        return DocumentMetadata(
            source_file=str(file_path.relative_to(self.documents_dir.parent)),
            insurance_provider=provider,
            document_type=doc_type,
            plan_level=None,  # Can be extracted from content if needed
        )
```

</details>

<details markdown="1">
<summary markdown="span">src/ingestion/chunker.py</summary>

```python
from typing import List
from langchain.text_splitter import MarkdownHeaderTextSplitter
from src.models.schemas import DocumentChunk, DocumentMetadata
import hashlib


class SmartChunker:
    """Chunk documents intelligently based on markdown structure."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Define headers to split on (preserves context)
        self.headers_to_split_on = [
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
            ("####", "h4"),
        ]

    def chunk_document(
        self,
        content: str,
        metadata: DocumentMetadata
    ) -> List[DocumentChunk]:
        """
        Chunk a document preserving markdown structure.

        Args:
            content: Document text
            metadata: Document metadata

        Returns:
            List of DocumentChunk objects
        """
        # Split by headers first
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on
        )
        header_chunks = splitter.split_text(content)

        chunks = []
        for i, doc in enumerate(header_chunks):
            # Generate unique chunk ID
            chunk_id = self._generate_chunk_id(
                metadata.source_file,
                i,
                doc.page_content
            )

            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                text=doc.page_content,
                metadata=metadata
            ))

        return chunks

    def _generate_chunk_id(self, source: str, index: int, content: str) -> str:
        """Generate a unique ID for a chunk."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{source}_{index}_{content_hash}"
```

</details>

**Acceptance Criteria**

- All markdown files are loaded successfully
- Chunks preserve section headers for context
- Metadata correctly extracted from file paths
- Each chunk has a unique ID

**Testing Strategy**

- Unit test: Load a single test markdown file
- Unit test: Verify chunk IDs are unique
- Unit test: Verify metadata extraction
- Integration test: Load all documents and verify count

---

### Step 2.2: Embeddings & Qdrant Upload

**Purpose / Scope**

Generate embeddings for document chunks and upload them to Qdrant vector database.

**Requirements**

- Use OpenAI embeddings (or Gemini as fallback)
- Create Qdrant collection with proper configuration
- Batch upload for efficiency
- Handle errors gracefully

**Implementation**

<details markdown="1">
<summary markdown="span">src/ingestion/embedder.py</summary>

```python
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.models.schemas import DocumentChunk
from src.config import OPENAI_API_KEY, GEMINI_API_KEY, QDRANT_HOST


class EmbeddingService:
    """Service for creating embeddings and uploading to Qdrant."""

    COLLECTION_NAME = "insurance_documents"
    EMBEDDING_DIM = 1536  # OpenAI ada-002 dimension

    def __init__(self, use_openai: bool = True):
        # Initialize embedding model
        if use_openai and OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=OPENAI_API_KEY
            )
            self.embedding_dim = 1536
        elif GEMINI_API_KEY:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=GEMINI_API_KEY
            )
            self.embedding_dim = 768
        else:
            raise ValueError("No API key found for embeddings")

        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(url=QDRANT_HOST)

    def create_collection(self, recreate: bool = False):
        """Create Qdrant collection."""
        if recreate:
            self.qdrant_client.delete_collection(self.COLLECTION_NAME)

        self.qdrant_client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=self.embedding_dim,
                distance=Distance.COSINE
            ),
        )

    def embed_and_upload(
        self,
        chunks: List[DocumentChunk],
        batch_size: int = 100
    ):
        """
        Embed chunks and upload to Qdrant.

        Args:
            chunks: List of document chunks
            batch_size: Number of chunks to process at once
        """
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            # Generate embeddings
            texts = [chunk.text for chunk in batch]
            embeddings = self.embeddings.embed_documents(texts)

            # Create Qdrant points
            points = []
            for chunk, embedding in zip(batch, embeddings):
                point = PointStruct(
                    id=chunk.chunk_id,
                    vector=embedding,
                    payload={
                        "text": chunk.text,
                        "source_file": chunk.metadata.source_file,
                        "insurance_provider": chunk.metadata.insurance_provider,
                        "document_type": chunk.metadata.document_type,
                        "plan_level": chunk.metadata.plan_level,
                    }
                )
                points.append(point)

            # Upload batch
            self.qdrant_client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points
            )

            print(f"Uploaded batch {i // batch_size + 1}: {len(points)} chunks")
```

</details>

**Acceptance Criteria**

- Qdrant collection is created successfully
- All chunks are embedded and uploaded
- Embeddings have correct dimensions
- Collection is queryable

**Testing Strategy**

- Integration test: Create collection and upload test chunks
- Integration test: Query collection and verify results
- Unit test: Verify embedding dimensions

---

### Step 2.3: Ingestion CLI Tool

**Purpose / Scope**

Create a command-line tool to run the ingestion pipeline.

**Requirements**

- Load, chunk, embed, and upload documents
- Show progress during ingestion
- Allow re-ingestion (recreate collection)

**Implementation**

<details markdown="1">
<summary markdown="span">scripts/ingest_documents.py</summary>

```python
#!/usr/bin/env python3
"""CLI tool to ingest insurance documents into Qdrant."""

import click
from src.ingestion.loader import InsuranceDocumentLoader
from src.ingestion.chunker import SmartChunker
from src.ingestion.embedder import EmbeddingService


@click.command()
@click.option('--recreate', is_flag=True, help='Recreate collection (delete existing)')
@click.option('--use-openai/--use-gemini', default=True, help='Use OpenAI or Gemini embeddings')
def ingest(recreate: bool, use_openai: bool):
    """Ingest insurance documents into Qdrant vector database."""

    click.echo("🔄 Loading documents...")
    loader = InsuranceDocumentLoader()
    documents = loader.load_all()
    click.echo(f"✅ Loaded {len(documents)} documents")

    click.echo("✂️  Chunking documents...")
    chunker = SmartChunker()
    all_chunks = []
    for content, metadata in documents:
        chunks = chunker.chunk_document(content, metadata)
        all_chunks.extend(chunks)
    click.echo(f"✅ Created {len(all_chunks)} chunks")

    click.echo("🚀 Embedding and uploading to Qdrant...")
    embedder = EmbeddingService(use_openai=use_openai)

    if recreate:
        click.echo("⚠️  Recreating collection...")
        embedder.create_collection(recreate=True)
    else:
        embedder.create_collection(recreate=False)

    embedder.embed_and_upload(all_chunks)
    click.echo("✅ Ingestion complete!")


if __name__ == '__main__':
    ingest()
```

</details>

**Acceptance Criteria**

- CLI runs without errors
- Progress is shown during ingestion
- Collection is populated with all chunks

**Testing Strategy**

- Manual test: Run CLI and verify Qdrant collection
- Integration test: Run ingestion and query collection

---

### Step 3.1: Qdrant Client Wrapper

**Purpose / Scope**

Create a clean interface for Qdrant retrieval operations.

**Requirements**

- Semantic search with filters
- Hybrid search (dense + sparse)
- Return results with metadata and scores

**Implementation**

<details markdown="1">
<summary markdown="span">src/retrieval/qdrant_client.py</summary>

```python
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain_openai import OpenAIEmbeddings
from src.models.schemas import RetrievedChunk, DocumentChunk, DocumentMetadata
from src.config import QDRANT_HOST, OPENAI_API_KEY


class QdrantRetriever:
    """Wrapper for Qdrant retrieval operations."""

    COLLECTION_NAME = "insurance_documents"

    def __init__(self):
        self.client = QdrantClient(url=QDRANT_HOST)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Semantic search in Qdrant.

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of retrieved chunks with scores
        """
        # Embed query
        query_vector = self.embeddings.embed_query(query)

        # Build filter if provided
        qdrant_filter = self._build_filter(filters) if filters else None

        # Search
        results = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter
        )

        # Convert to RetrievedChunk objects
        retrieved = []
        for result in results:
            chunk = DocumentChunk(
                chunk_id=str(result.id),
                text=result.payload["text"],
                metadata=DocumentMetadata(
                    source_file=result.payload["source_file"],
                    insurance_provider=result.payload["insurance_provider"],
                    document_type=result.payload["document_type"],
                    plan_level=result.payload.get("plan_level"),
                )
            )
            retrieved.append(RetrievedChunk(
                chunk=chunk,
                score=result.score
            ))

        return retrieved

    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from dict."""
        conditions = []

        for key, value in filters.items():
            conditions.append(
                FieldCondition(key=key, match=MatchValue(value=value))
            )

        return Filter(must=conditions)
```

</details>

**Acceptance Criteria**

- Search returns relevant results
- Filters work correctly
- Results include all necessary metadata

**Testing Strategy**

- Integration test: Search for known content
- Integration test: Test filters (by provider, document type)
- Unit test: Filter building logic

---

### Step 4.1-4.6: LangGraph Workflow

**Purpose / Scope**

Build the complete agent workflow using LangGraph for orchestration.

**Requirements**

- State management for query flow
- Nodes for: query analysis, retrieval, reranking, generation, citation
- Conditional edges based on retrieval quality
- Streaming support for responses

**Implementation**

<details markdown="1">
<summary markdown="span">src/graph/workflow.py (simplified example)</summary>

```python
from langgraph.graph import StateGraph, END
from src.models.schemas import AgentState
from src.graph.nodes import (
    analyze_query_node,
    retrieve_node,
    rerank_node,
    generate_answer_node,
    add_citations_node
)


def create_insurance_agent():
    """Create the LangGraph workflow for insurance advice."""

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyze_query", analyze_query_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("rerank", rerank_node)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("add_citations", add_citations_node)

    # Define edges
    workflow.set_entry_point("analyze_query")
    workflow.add_edge("analyze_query", "retrieve")
    workflow.add_edge("retrieve", "rerank")
    workflow.add_edge("rerank", "generate_answer")
    workflow.add_edge("generate_answer", "add_citations")
    workflow.add_edge("add_citations", END)

    # Compile
    return workflow.compile()
```

</details>

**Acceptance Criteria**

- Graph executes end-to-end without errors
- Each node properly updates state
- Final answer includes sources
- State is properly typed

**Testing Strategy**

- Integration test: Run full workflow with test query
- Unit test: Each node in isolation
- Integration test: Verify state transitions

---

### Step 5.1: CLI Interface

**Purpose / Scope**

Interactive CLI for querying the insurance agent.

**Requirements**

- REPL-style interface
- Show sources with answers
- Pretty formatting

**Implementation**

Use `click` or `rich` for interactive CLI with markdown rendering.

**Acceptance Criteria**

- Interactive queries work
- Sources are clearly displayed
- Errors are handled gracefully

**Testing Strategy**

- Manual test: Interactive session
- Integration test: Automated query/response

---

### Step 6.1-6.3: Testing & Evaluation

**Purpose / Scope**

Comprehensive testing and evaluation metrics.

**Requirements**

- Unit tests for all components
- Integration tests for workflows
- Evaluation metrics: answer quality, retrieval precision, source accuracy

**Implementation**

Use `pytest` for testing, create evaluation dataset with ground-truth Q&A pairs.

**Acceptance Criteria**

- 90%+ code coverage
- All tests pass
- Retrieval precision > 0.8
- Answer quality evaluated by human review

**Testing Strategy**

- Unit tests: All modules
- Integration tests: End-to-end workflows
- Evaluation: Gold standard Q&A dataset

---

## 5 Technical Standards

| Area               | Standard                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------- |
| Code Style         | Ruff linting with 0 violations                                                              |
| Type Hints         | Full type hints on all functions, validated with mypy                                       |
| Package Management | Use `uv` for dependency management, run via `uv run`, keep dependencies in `pyproject.toml` |
| Docstrings         | Google-style docstrings for all public functions/classes                                    |
| Error Handling     | Explicit exception handling, no bare `except` clauses                                       |
| Logging            | Use Python `logging` module, levels: DEBUG (dev), INFO (prod)                               |
| Environment Vars   | All config in `.env`, loaded via `python-dotenv`                                            |
| Database           | Qdrant collections with proper indexes and metadata                                         |
| Testing            | pytest, 90%+ coverage, unit + integration tests                                             |
| Docker             | Multi-stage builds, dev/prod configs, health checks for all services                        |
| Security           | No secrets in code, use environment variables, audit dependencies regularly                 |
| Git Workflow       | Feature branches, meaningful commits, PR reviews before merge                               |

---

## 6 Success Metrics

- **Functional**

  - Retrieval precision ≥ 0.85 (relevant chunks in top 5)
  - Source attribution accuracy ≥ 95% (correct document cited)
  - Answer completeness: User finds answer in ≥ 90% of queries

- **Performance**

  - Query response time < 3 seconds (end-to-end)
  - Qdrant search latency < 100ms
  - Embedding generation < 500ms per query

- **Quality**
  - Human evaluation: Answer quality ≥ 4.0/5.0
  - Hallucination rate < 5% (verified by source check)
  - User satisfaction: CSAT ≥ 4.5/5.0

---

## 7 Risk Mitigation

| Risk Type   | Description                             | Mitigation                                                              | Owner    |
| ----------- | --------------------------------------- | ----------------------------------------------------------------------- | -------- |
| Technical   | Qdrant downtime affects all queries     | Implement fallback to local vector store, add health checks             | DevOps   |
| Technical   | Embeddings API rate limits              | Add retry logic with exponential backoff, consider local embeddings     | Dev      |
| Technical   | LLM hallucinations despite RAG          | Add source verification step, confidence scoring, citation requirements | Dev      |
| Business    | Outdated insurance documents            | Implement document versioning, automated update detection               | Product  |
| Business    | Incorrect advice leads to user issues   | Add disclaimers, human-in-the-loop for critical queries                 | Legal    |
| Integration | Docker networking issues in dev/prod    | Use Docker Compose networks, document setup thoroughly                  | DevOps   |
| Data        | Poor chunking reduces retrieval quality | Evaluate multiple chunking strategies, tune chunk size empirically      | Dev      |
| Security    | API keys exposed in logs or errors      | Sanitize logs, use secret management, never log full requests           | Security |

---

## Notes

- This plan assumes you're building from scratch. Adjust steps based on what already exists.
- Consider adding a web interface (FastAPI) in a future iteration.
- For production, add monitoring (Prometheus), logging aggregation (ELK), and alerting.
- Evaluate cost of OpenAI API calls and consider fallback to open-source embeddings/LLMs.
