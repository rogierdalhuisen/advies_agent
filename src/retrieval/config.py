"""Configuration for the retrieval module."""
import sys
from pathlib import Path

# 1. Define the directory that CONTAINS the 'src' folder
# If the file is in src/retrieval/, then .parent.parent is the project root
RETRIEVAL_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = RETRIEVAL_ROOT.parent.parent 

# 2. Add that root to the system path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 3. Now import using the actual package name 'src'
from src.config import QDRANT_HOST, OPENAI_API_KEY

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-large"
SPARSE_EMBEDDING_MODEL = "Qdrant/bm25"

# Collection configuration
COLLECTION_NAME = "insurance_docs_text-embedding-3-large"

# Vector store configuration
DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"

# Export shared config
QDRANT_URL = QDRANT_HOST
OPENAI_KEY = OPENAI_API_KEY
