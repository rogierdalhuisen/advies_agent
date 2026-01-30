"""Configuration for the reranker module."""
import sys
import os
from pathlib import Path

# Ensure project root is in path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import main secrets
# Ensure SILICONFLOW_API_KEY is in your .env and src/config.py
from src.config import SILICONFLOW_API_KEY

# --- Reranker Settings ---

RERANKER_PROVIDER = "siliconflow"
RERANKER_MODEL = "Qwen/Qwen3-Reranker-8B"

# SiliconFlow Rerank Endpoint
RERANKER_API_URL = "https://api.siliconflow.com/v1/rerank" 
RERANKER_API_KEY = SILICONFLOW_API_KEY