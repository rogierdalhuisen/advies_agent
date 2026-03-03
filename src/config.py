import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import true

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
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")

LANGSMITH_TRACING=true                                                                                                                                                                                  
LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY")                 
LANGSMITH_PROJECT=os.getenv("LANGSMITH_PROJECT", "joho")
LANGSMITH_ENDPOINT=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

# Hosts
# In Docker: QDRANT_HOST=qdrant (service name)
# Outside Docker: QDRANT_HOST=http://localhost:6333 (exposed port)
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://localhost:6333")

# PostgreSQL Database (external adviesaanvragen database)
# Supports POSTGRES_*, POSTEGRES_* (legacy typo), and DB_* variable names
POSTGRES_HOST = os.getenv("POSTGRES_HOST") or os.getenv("POSTEGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT") or os.getenv("POSTEGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB") or os.getenv("POSTEGRES_NAME") or os.getenv("DB_NAME", "")
POSTGRES_USER = os.getenv("POSTGRES_USER") or os.getenv("POSTEGRES_USER") or os.getenv("DB_USER", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD") or os.getenv("POSTEGRES_PASSWORD") or os.getenv("DB_PASSWORD", "")

def get_postgres_url() -> str:
    """Build PostgreSQL connection URL from environment variables."""
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"




