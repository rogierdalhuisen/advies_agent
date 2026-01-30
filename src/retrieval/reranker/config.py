"""Configuration for the reranker module."""
import sys
from pathlib import Path
import os

# Ensure project root is in path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import main secrets
from src.config import HUGGINGFACE_API_KEY, COHERE_API_KEY

# --- Reranker Settings ---

# Option 1: HuggingFace Inference Endpoint (e.g. for Qwen-Reranker)
# Leave URL empty if using a standard public model via API
RERANKER_PROVIDER = "huggingface" 
RERANKER_MODEL = "BAAI/bge-reranker-large" # or "Qwen/Qwen2.5-Math-RM-72B" etc.
RERANKER_API_URL = "https://api-inference.huggingface.co/models/" + RERANKER_MODEL
RERANKER_API_KEY = HUGGINGFACE_API_KEY

# Option 2: Cohere (Alternative)
# RERANKER_PROVIDER = "cohere"
# RERANKER_MODEL = "rerank-english-v3.0"
# RERANKER_API_KEY = COHERE_API_KEY