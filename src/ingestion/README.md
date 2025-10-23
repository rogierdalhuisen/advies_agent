# Ingestion Scripts

This directory contains scripts for ingesting documents into the Qdrant vector database.

## index_dekkingen.py

Processes insurance coverage (dekkingen) documents using hierarchical chunking and stores them as embeddings in Qdrant.

### Running the Script

#### Option 1: Inside Docker (Recommended for Production)

1. **Rebuild the Docker image** (after adding new dependencies):
   ```bash
   ./dev.sh rebuild
   ```

2. **Run the ingestion script** inside the container:
   ```bash
   # Using the agent container (when it's running)
   ./dev.sh shell
   python -m src.ingestion.index_dekkingen

   # OR using the jupyter container
   docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec jupyter python -m src.ingestion.index_dekkingen
   ```

#### Option 2: Outside Docker (For Development/Testing)

This works because Qdrant's ports are exposed to your host machine:

```bash
source .venv/bin/activate
python -m src.ingestion.index_dekkingen
```

**Note**: This uses `QDRANT_HOST=http://localhost:6333` instead of the Docker service name.

### Configuration

All configuration is at the top of `index_dekkingen.py`:

```python
COLLECTION_NAME = "dekkingen"
EMBEDDING_MODEL_NAME = "models/embedding-001"  # Google's embedding model
EMBEDDING_DIMENSION = 768
DISTANCE_METRIC = Distance.COSINE
```

To use a different embedding model:

1. Change `EMBEDDING_MODEL_NAME` and `EMBEDDING_DIMENSION`
2. Optionally swap the embedding provider:
   - Current: `GoogleGenerativeAIEmbeddings` (Gemini)
   - Alternatives: `OpenAIEmbeddings`, `HuggingFaceEmbeddings`, etc.

### How It Works

1. **Load Documents**: Reads all `.md` files from `data/documents/dekkingen/`
2. **Hierarchical Chunking**: Splits by markdown headers (H1-H4) using `MarkdownHeaderTextSplitter`
3. **Metadata Extraction**: Captures:
   - Header hierarchy (header_1, header_2, etc.)
   - Document name
   - Company (extracted from filename)
   - Ingestion timestamp
   - File path
4. **Embedding & Indexing**: Creates embeddings and stores in Qdrant

### Environment Variables

Required in `.env`:

- `GEMINI_API_KEY`: Google API key for embeddings
- `QDRANT_HOST`: Qdrant connection (auto-configured via docker-compose)

### Verifying the Data

Check Qdrant UI:
```bash
./dev.sh qdrant-ui
```

Or query via API:
```bash
# List collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/dekkingen

# View sample points
curl -X POST http://localhost:6333/collections/dekkingen/points/scroll \
  -H 'Content-Type: application/json' \
  -d '{"limit": 5, "with_payload": true, "with_vector": false}'
```
