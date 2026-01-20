#!/usr/bin/env python3
"""CLI tool to scrape insurance company websites and save as markdown.

This script uses crawl4ai to scrape insurance documentation pages and
Gemini Flash to extract clean markdown content. It's designed to be run
monthly to keep the knowledge base up-to-date.

Usage:
    # Scrape all providers
    python scripts/scrape_insurance_data.py

    # Scrape specific provider
    python scripts/scrape_insurance_data.py --provider goudse_expat_pakket

    # Dry run (don't save files)
    python scripts/scrape_insurance_data.py --dry-run
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from src.scraping import InsuranceScraper
from src.scraping.config import get_all_configs, get_provider_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    '--provider',
    '-p',
    help='Specific provider slug to scrape (e.g., goudse_expat_pakket). Scrapes all if not specified.'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Run scraper without saving files to disk'
)
@click.option(
    '--list-providers',
    is_flag=True,
    help='List all configured providers and exit'
)
def main(provider: str, dry_run: bool, list_providers: bool):
    """Scrape insurance company websites and save as markdown."""

    # List providers and exit
    if list_providers:
        click.echo("📋 Configured insurance providers:\n")
        all_configs = get_all_configs()

        for config in all_configs:
            click.echo(f"  • {config.provider_name} ({config.provider_slug})")
            if config.url:
                click.echo(f"    URL: {config.url}")
            else:
                click.echo(f"    ⚠️  No URL configured yet (add to src/scraping/config.py)")
            if config.description:
                click.echo(f"    {config.description}")
            click.echo()

        return

    # Start scraping
    click.echo("🚀 Starting insurance data scraper\n")

    if dry_run:
        click.echo("⚠️  DRY RUN MODE - Files will not be saved\n")

    if provider:
        click.echo(f"📍 Scraping provider: {provider}\n")
        config = get_provider_config(provider)

        if not config:
            click.echo(f"❌ Provider not found: {provider}", err=True)
            click.echo("\nRun with --list-providers to see all available providers")
            sys.exit(1)

        # Check if URL is configured
        if not config.url:
            click.echo(f"⚠️  No URL configured for {provider}")
            click.echo("Add URL to src/scraping/config.py before scraping")
            sys.exit(1)

    else:
        click.echo("📍 Scraping all providers\n")

    # Run scraper
    try:
        scraper = InsuranceScraper()

        if provider:
            url, content = asyncio.run(scraper.scrape_provider(provider, save_to_disk=not dry_run))
            display_result(provider, url, content)
        else:
            results = asyncio.run(scraper.scrape_all_providers(save_to_disk=not dry_run))
            for provider_slug, (url, content) in results.items():
                display_result(provider_slug, url, content)

        click.echo("\n✅ Scraping complete!")

        if dry_run:
            click.echo("\n💡 Run without --dry-run to save files to disk")

    except Exception as e:
        click.echo(f"\n❌ Error during scraping: {e}", err=True)
        logger.error("Scraping failed", exc_info=True)
        sys.exit(1)


def display_result(provider_slug: str, url: Optional[str], content: Optional[str]):
    """Display scraping result for a provider."""
    click.echo(f"\n📦 {provider_slug}:")

    if not url:
        click.echo("  ⚠️  No URL configured")
        return

    if content:
        click.echo(f"  ✅ {url} ({len(content)} chars)")
    else:
        click.echo(f"  ❌ {url} [FAILED]")


if __name__ == '__main__':
    main()
