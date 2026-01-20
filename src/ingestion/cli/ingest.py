#!/usr/bin/env python3
"""
CLI interface for the ingestion pipeline.

Usage:
    # Full ingestion (all documents)
    python -m src.ingestion.cli.ingest

    # With custom config file
    python -m src.ingestion.cli.ingest --config config/custom.yaml

    # Filter by insurance provider
    python -m src.ingestion.cli.ingest --insurance goudse_expat_pakket

    # Filter by document pattern
    python -m src.ingestion.cli.ingest --pattern "webpage_*.md"

    # Inspect collection
    python -m src.ingestion.cli.ingest --inspect
"""

import click
from pathlib import Path
from src.ingestion.pipelines.ingestion_pipeline import IngestionPipeline
from src.ingestion.config.settings import load_settings
from src.ingestion.indexers.qdrant_indexer import QdrantIndexer
from src.ingestion.embedders.factory import EmbedderFactory


@click.group()
def cli():
    """Insurance documents ingestion CLI"""
    pass


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to YAML config file (optional, uses defaults if not provided)"
)
@click.option(
    "--insurance",
    type=str,
    help="Insurance provider folder name to filter (e.g., goudse_expat_pakket)"
)
@click.option(
    "--pattern",
    type=str,
    help="Glob pattern to filter documents (e.g., 'webpage_*.md')"
)
def run(config: str, insurance: str, pattern: str):
    """
    Run the ingestion pipeline.

    Loads, chunks, embeds, and indexes documents into Qdrant.
    """
    try:
        # Initialize pipeline
        pipeline = IngestionPipeline(config_file=config)

        # Run pipeline
        result = pipeline.run(
            document_pattern=pattern,
            insurance_provider=insurance
        )

        if "error" in result:
            click.echo(f"❌ Error: {result['error']}", err=True)
            exit(1)

    except Exception as e:
        click.echo(f"❌ Pipeline failed: {e}", err=True)
        import traceback
        traceback.print_exc()
        exit(1)


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to YAML config file"
)
def inspect(config: str):
    """
    Inspect the Qdrant collection.

    Shows collection statistics and configuration.
    """
    try:
        # Load settings
        settings = load_settings(config)

        # Create indexer
        embeddings = EmbedderFactory.create(settings.embedding)
        embedding_dim = EmbedderFactory.get_embedding_dimension(settings.embedding)
        collection_name = settings.get_collection_name()

        indexer = QdrantIndexer(
            embeddings=embeddings,
            collection_settings=settings.collection,
            collection_name=collection_name,
            embedding_dimension=embedding_dim,
            enable_deduplication=False
        )

        # Get collection info
        info = indexer.get_collection_info()

        click.echo("\n" + "=" * 60)
        click.echo("QDRANT COLLECTION INFO")
        click.echo("=" * 60)

        if "error" in info:
            click.echo(f"❌ Error: {info['error']}")
        else:
            click.echo(f"Collection name: {info.get('name')}")
            click.echo(f"Points count: {info.get('points_count')}")
            click.echo(f"Vectors count: {info.get('vectors_count')}")
            click.echo(f"Indexed vectors: {info.get('indexed_vectors_count')}")
            click.echo(f"Status: {info.get('status')}")

        click.echo("=" * 60)

        # Show settings
        click.echo("\nCONFIGURATION")
        click.echo("-" * 60)
        click.echo(f"Embedding provider: {settings.embedding.provider}")
        click.echo(f"Embedding model: {settings.embedding.model_name}")
        click.echo(f"Embedding dimension: {settings.embedding.dimension}")
        click.echo(f"Chunking strategy: {settings.chunking.strategy}")
        click.echo(f"Max chunk size: {settings.chunking.max_chunk_size}")
        click.echo(f"Use sparse vectors: {settings.collection.use_sparse}")
        click.echo("=" * 60 + "\n")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        exit(1)


@cli.command()
def validate():
    """
    Validate configuration and dependencies.

    Checks that all required settings and API keys are present.
    """
    try:
        from src.config import OPENAI_API_KEY, GEMINI_API_KEY, QDRANT_HOST

        click.echo("\n" + "=" * 60)
        click.echo("CONFIGURATION VALIDATION")
        click.echo("=" * 60)

        # Check API keys
        click.echo("\nAPI Keys:")
        click.echo(f"  OpenAI: {'✅ Set' if OPENAI_API_KEY else '❌ Missing'}")
        click.echo(f"  Gemini: {'✅ Set' if GEMINI_API_KEY else '❌ Missing'}")

        # Check Qdrant
        click.echo(f"\nQdrant:")
        click.echo(f"  Host: {QDRANT_HOST}")

        # Try to connect to Qdrant
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(url=QDRANT_HOST)
            collections = client.get_collections()
            click.echo(f"  Status: ✅ Connected ({len(collections.collections)} collections)")
        except Exception as e:
            click.echo(f"  Status: ❌ Connection failed: {e}")

        # Load settings
        settings = load_settings()
        click.echo(f"\nSettings:")
        click.echo(f"  Documents dir: {settings.documents_dir}")
        click.echo(f"  Chunks output: {settings.chunks_output_dir}")

        # Check if documents directory exists
        docs_path = Path(settings.documents_dir)
        if docs_path.exists():
            md_files = list(docs_path.rglob("*.md"))
            click.echo(f"  Found: ✅ {len(md_files)} markdown files")
        else:
            click.echo(f"  Status: ❌ Directory not found: {docs_path}")

        click.echo("=" * 60 + "\n")

    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    cli()
