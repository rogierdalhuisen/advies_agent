import os
from pathlib import Path
from dotenv import load_dotenv

# .parent is de 'src' map
SRC_ROOT = Path(__file__).resolve().parent

# .parent van de 'src' map is de project root
PROJECT_ROOT = SRC_ROOT.parent

# Laad de .env bestand in de project root
load_dotenv(PROJECT_ROOT / ".env")

# Definieer je datamap
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"

#Api keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

#hosts
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://localhost:6333")




