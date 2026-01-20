# Insurance Documents Ingestion Pipeline

Simple, modular pipeline for ingesting insurance documents into Qdrant with hybrid retrieval.

## Quick Start

```bash
# 1. Add to .env
OPENROUTER_API_KEY=your_key_here
QDRANT_HOST=http://localhost:6333

# 2. Start Qdrant
./dev.sh up

# 3. Run ingestion
uv run python -m src.ingestion run
```

## Features

- ✅ **OpenRouter Integration** - Access any embedding model through one API
- ✅ **Auto Collection Naming** - Each model gets its own collection automatically
- ✅ **Hybrid Chunking** - Header-based + size-based splitting
- ✅ **Hybrid Retrieval** - Dense + sparse (BM25) embeddings
- ✅ **Smart Deduplication** - Content-hash based change detection

## Configuration

Default (in `src/ingestion/config/settings.py`):
```python
provider: "openrouter"
model_name: "openai/text-embedding-3-large"
dimension: 3072
base_name: "insurance_docs"  # Auto-appends model name
```

Override with YAML (`config/ingestion.yaml`):
```yaml
embedding:
  provider: openrouter
  model_name: openai/text-embedding-3-large
  dimension: 3072

collection:
  base_name: insurance_docs

chunking:
  strategy: hybrid
  max_chunk_size: 1000
  chunk_overlap: 100

documents_dir: data/documents
enable_deduplication: true
save_chunks_to_disk: true
```

## CLI Commands

```bash
# Full ingestion
uv run python -m src.ingestion run

# Filter by insurance
uv run python -m src.ingestion run --insurance goudse_expat_pakket

# Filter by pattern (e.g., only webpages)
uv run python -m src.ingestion run --pattern "webpage_*.md"

# With custom config
uv run python -m src.ingestion run --config config/my_model.yaml

# Inspect collection
uv run python -m src.ingestion inspect

# Validate setup
uv run python -m src.ingestion validate
```

## Testing Different Models

**Collections are auto-named: `{base_name}_{model_name}`**

This means each model gets its own collection automatically - no conflicts!

### Example: Test 3 Models

```bash
# 1. Test OpenAI Large (default)
uv run python -m src.ingestion run
# Creates: insurance_docs_openai_text-embedding-3-large

# 2. Test Google
cat > /tmp/google.yaml << 'EOF'
embedding:
  provider: openrouter
  model_name: google/text-embedding-004
  dimension: 768
collection:
  base_name: insurance_docs
chunking:
  strategy: hybrid
  max_chunk_size: 1000
documents_dir: data/documents
enable_deduplication: true
EOF

uv run python -m src.ingestion run --config /tmp/google.yaml
# Creates: insurance_docs_google_text-embedding-004

# 3. Test OpenAI Small
cat > /tmp/small.yaml << 'EOF'
embedding:
  provider: openrouter
  model_name: openai/text-embedding-3-small
  dimension: 1536
collection:
  base_name: insurance_docs
chunking:
  strategy: hybrid
  max_chunk_size: 1000
documents_dir: data/documents
enable_deduplication: true
EOF

uv run python -m src.ingestion run --config /tmp/small.yaml
# Creates: insurance_docs_openai_text-embedding-3-small

# Now you have 3 collections to compare!
```

## Available Models (via OpenRouter)

**OpenAI:**
- `openai/text-embedding-3-large` (3072d) - Best quality
- `openai/text-embedding-3-small` (1536d) - Good balance, lower cost

**Google:**
- `google/text-embedding-004` (768d) - Cost effective

**Others:**
- Check [OpenRouter models](https://openrouter.ai/models) for more options

### Direct Providers (Fallback)

```yaml
# Direct OpenAI (no OpenRouter)
embedding:
  provider: openai
  model_name: text-embedding-3-large
  dimension: 3072

# Direct Gemini (no OpenRouter)
embedding:
  provider: gemini
  model_name: models/embedding-001
  dimension: 768
```

## Update Strategies

### Monthly Updates (Webpages)
```bash
uv run python -m src.ingestion run --pattern "webpage_*.md"
```

### Yearly Updates (Policy Docs)
```bash
uv run python -m src.ingestion run --insurance goudse_expat_pakket
```

### After Manual Changes
```bash
uv run python -m src.ingestion run
```

Deduplication automatically removes old chunks and indexes fresh ones.

## Comparing Models

After indexing with multiple models, compare their collections:

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

# List all collections
for col in client.get_collections().collections:
    if col.name.startswith("insurance_docs_"):
        print(f"{col.name}: {col.points_count} chunks")

# Query specific collection
results = client.search(
    collection_name="insurance_docs_openai_text-embedding-3-large",
    query_vector=your_embedding,
    limit=5
)
```

## Metadata Structure

Each chunk includes rich metadata:

```json
{
  "insurance_provider": "goudse_expat_pakket",
  "company_display_name": "Goudse Expat Package",
  "document_type": "conditions",
  "document_name": "EN 2025 - Conditions.md",
  "version_date": "2026-01-20",
  "is_webpage": false,
  "filepath": "data/documents/.../file.md",
  "document_id": "abc123...",
  "content_hash": "def456...",
  "header_1": "Coverage",
  "header_2": "Medical Expenses",
  "chunk_index": 5
}
```

## Troubleshooting

### API Key Missing
```bash
# Ensure in .env
OPENROUTER_API_KEY=your_key_here

# Validate
uv run python -m src.ingestion validate
```

### Qdrant Not Running
```bash
./dev.sh up
```

### Collection Name?
```bash
# Check actual collection name
uv run python -m src.ingestion inspect --config your_config.yaml
```

## Architecture

```
Documents → Load → Chunk → Embed → Index
              ↓       ↓       ↓       ↓
          Markdown  Hybrid  OpenRouter Qdrant
                           (any model) (hybrid)
```

**Components:**
- **Loaders** - Extract text + metadata from markdown
- **Chunkers** - Split by headers, then by size if needed
- **Embedders** - Generate embeddings via OpenRouter
- **Indexers** - Store in Qdrant with deduplication

## Development

```bash
# Test with sample data
uv run python -m src.ingestion run --insurance goudse_expat_pakket

# Inspect results
uv run python -m src.ingestion inspect

# Check saved chunks
ls data/documents/chunks/goudse_expat_pakket/
cat data/documents/chunks/goudse_expat_pakket/chunk_0001.txt
```

## What Changed (Cleanup)

**Simplified from previous version:**
- ✅ Removed complex multi-model scripts
- ✅ Removed 6 old/redundant files
- ✅ Centralized on OpenRouter
- ✅ Auto-naming always enabled
- ✅ Cleaner, easier to understand

**Benefits:**
- 50% less code
- Single clear path
- Still flexible for testing models
