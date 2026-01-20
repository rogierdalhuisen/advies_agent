# Insurance Documents Ingestion Pipeline

A modular, configurable pipeline for ingesting insurance documents into Qdrant vector database with hybrid retrieval (dense + sparse embeddings).

## Features

- **Modular Architecture**: Separate components for loading, chunking, embedding, and indexing
- **Hybrid Chunking**: Hierarchical (header-based) + size-based splitting for optimal chunk sizes
- **Hybrid Retrieval**: Dense (semantic) + sparse (BM25) embeddings for better search quality
- **Multiple Embedding Providers**: OpenAI, Google Gemini, OpenRouter support via LangChain
- **Automatic Deduplication**: Content-hash based change detection
- **Rich Metadata**: Insurance provider, document type, version dates, header hierarchy
- **Flexible Configuration**: YAML config + environment variables
- **CLI Interface**: Easy-to-use command-line tools

## Architecture

```
Document Loading → Chunking → Embedding → Indexing
     ↓                ↓           ↓          ↓
  Markdown      Hierarchical   OpenAI     Qdrant
   Loader       + Size-based   Embeddings  (Hybrid)
```

### Components

- **Loaders** (`loaders/`): Load documents with metadata extraction
- **Chunkers** (`chunkers/`): Split documents into semantic chunks
- **Embedders** (`embedders/`): Generate embeddings from multiple providers
- **Indexers** (`indexers/`): Index chunks into Qdrant with deduplication
- **Pipelines** (`pipelines/`): Orchestrate the complete flow
- **CLI** (`cli/`): Command-line interface

## Configuration

### Environment Variables (`.env`)

```bash
# API Keys (required)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...

# Qdrant (required)
QDRANT_HOST=http://qdrant:6333
```

### Settings File (Optional: `config/ingestion.yaml`)

```yaml
embedding:
  provider: openai  # Options: openai, gemini, openrouter
  model_name: text-embedding-3-large
  dimension: 3072
  batch_size: 100

chunking:
  strategy: hybrid  # Options: hierarchical, hybrid
  max_chunk_size: 1000
  chunk_overlap: 100
  size_threshold: 800

collection:
  name: insurance_documents
  use_sparse: true  # Enable hybrid retrieval
  sparse_model: Qdrant/bm25

documents_dir: data/documents
chunks_output_dir: data/documents/chunks
enable_deduplication: true
save_chunks_to_disk: true
```

## Usage

### CLI Commands

#### 1. Run Full Ingestion

Index all documents:

```bash
# Using defaults
uv run python -m src.ingestion run

# With custom config
uv run python -m src.ingestion run --config config/custom.yaml
```

#### 2. Filter by Insurance Provider

Index documents for a specific insurance:

```bash
uv run python -m src.ingestion run --insurance goudse_expat_pakket
```

#### 3. Filter by Document Pattern

Index only webpage documents (monthly updates):

```bash
uv run python -m src.ingestion run --pattern "webpage_*.md"
```

#### 4. Inspect Collection

View collection statistics and configuration:

```bash
uv run python -m src.ingestion inspect
```

#### 5. Validate Configuration

Check that all settings and dependencies are correctly configured:

```bash
uv run python -m src.ingestion validate
```

### Programmatic Usage

```python
from src.ingestion.pipelines.ingestion_pipeline import IngestionPipeline

# Initialize with defaults
pipeline = IngestionPipeline()

# Or with custom config
pipeline = IngestionPipeline(config_file="config/custom.yaml")

# Run full ingestion
result = pipeline.run()

# Run with filters
result = pipeline.run(insurance_provider="goudse_expat_pakket")
result = pipeline.run(document_pattern="webpage_*.md")

# Check results
print(f"Indexed {result['chunks_created']} chunks")
```

## Update Strategies

### Monthly Updates (Webpages)

Webpages are updated monthly (`webpage_YYYYMMDD.md`):

```bash
# Index only new webpages
uv run python -m src.ingestion run --pattern "webpage_*.md"
```

Deduplication automatically removes old versions of the same document.

### Yearly Updates (Policy Documents)

Policy documents change annually. To update:

```bash
# Re-index specific insurance
uv run python -m src.ingestion run --insurance goudse_expat_pakket

# Or re-index all
uv run python -m src.ingestion run
```

### Manual Changes

After editing documents:

```bash
# Re-index everything (deduplication handles changes)
uv run python -m src.ingestion run
```

## Metadata Structure

Each chunk includes rich metadata for filtering:

```json
{
  "insurance_provider": "goudse_expat_pakket",
  "company_display_name": "Goudse Expat Package",
  "document_type": "conditions",
  "document_name": "EN 2025 - Conditions.md",
  "version_date": "2026-01-20",
  "is_webpage": false,
  "filepath": "data/documents/goudse_expat_pakket/conditions.md",
  "document_id": "abc123...",
  "content_hash": "def456...",
  "ingestion_timestamp": "2026-01-20T14:30:00",
  "header_1": "Coverage",
  "header_2": "Medical Expenses",
  "header_3": "Pregnancy and Childbirth",
  "chunk_index": 5,
  "is_sub_chunk": false
}
```

## Troubleshooting

### API Key Errors

Ensure `.env` file has correct keys:

```bash
# Check validation
uv run python -m src.ingestion validate
```

### Qdrant Connection Errors

Ensure Qdrant is running:

```bash
./dev.sh up
```

## Development

### Testing

Test with a single insurance provider:

```bash
uv run python -m src.ingestion run --insurance goudse_expat_pakket
```

Inspect results:

```bash
uv run python -m src.ingestion inspect
```

Check saved chunks:

```bash
ls -la data/documents/chunks/goudse_expat_pakket/
cat data/documents/chunks/goudse_expat_pakket/chunk_0001.txt
```

## Legacy Script

The old `index_dekkingen.py` is still available but deprecated. Please use the new modular pipeline instead.
