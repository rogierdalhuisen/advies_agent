"""
Make ingestion module directly executable.

Usage:
    python -m src.ingestion [command] [options]
"""

from src.ingestion.cli.ingest import cli

if __name__ == "__main__":
    cli()
