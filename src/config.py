import os
from pathlib import Path

# __file__ is het pad naar dit config.py bestand
# .resolve() maakt het een absoluut pad
# .parent is de 'src' map
SRC_ROOT = Path(__file__).resolve().parent

# .parent van de 'src' map is de project root
PROJECT_ROOT = SRC_ROOT.parent

# Definieer je datamap
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"

# Optioneel: Je kunt hier ook andere configuratie (zoals API keys)
# laden uit environment variables
# QDRANT_HOST = os.environ.get("QDRANT_HOST", "http://qdrant_db:6333")