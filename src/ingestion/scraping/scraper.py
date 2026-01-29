"""Web scraper for insurance company websites using crawl4ai.

This module handles the actual web scraping of insurance documentation pages.
It uses crawl4ai for robust web scraping and the LLM parser to extract clean content.
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import asyncio

try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    AsyncWebCrawler = None
    logging.warning("crawl4ai not installed. Run: pip install crawl4ai")

from .config import InsuranceURLConfig, get_all_configs, get_provider_config, get_all_provider_slugs
from .llm_parser import LLMContentParser
from src.config import DOCUMENTS_DIR

logger = logging.getLogger(__name__)


class InsuranceScraper:
    """Scrape insurance websites and save as markdown documents."""

    def __init__(self, parser: Optional[LLMContentParser] = None):
        """Initialize the scraper.

        Args:
            parser: LLM parser to use (creates default if not provided)
        """
        if AsyncWebCrawler is None:
            raise ImportError(
                "crawl4ai is required for scraping. "
                "Install it with: pip install crawl4ai"
            )

        self.parser = parser or LLMContentParser()
        self.output_dir = DOCUMENTS_DIR
        logger.info(f"Initialized scraper with output dir: {self.output_dir}")

    async def scrape_url(
        self,
        url: str,
        provider_name: str,
    ) -> Optional[str]:
        """Scrape a single URL and extract markdown content.

        Args:
            url: URL to scrape
            provider_name: Insurance provider name

        Returns:
            Extracted markdown content, or None if scraping failed
        """
        try:
            logger.info(f"Scraping {url}")

            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(url=url)

                if not result.success:
                    logger.error(f"Failed to scrape {url}: {result.error_message}")
                    return None

                # Get HTML content
                html_content = result.html

                if not html_content:
                    logger.error(f"No HTML content returned from {url}")
                    return None

                logger.info(f"Successfully scraped {url} ({len(html_content)} chars)")

                # Parse HTML to markdown using LLM
                markdown_content = self.parser.parse_with_context(
                    html_content=html_content,
                    url=url,
                    provider_name=provider_name,
                    document_type="webpage"  # Always "webpage" to indicate source
                )

                return markdown_content

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}", exc_info=True)
            return None

    def save_markdown(
        self,
        content: str,
        provider_slug: str,
        filename: Optional[str] = None
    ) -> Path:
        """Save markdown content to file.

        Args:
            content: Markdown content to save
            provider_slug: Provider slug (e.g., "goudse_expat_pakket")
            filename: Optional custom filename (default: webpage_{timestamp}.md)

        Returns:
            Path to saved file
        """
        # Create provider directory
        provider_dir = self.output_dir / provider_slug
        provider_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"webpage_{timestamp}.md"

        # Save file
        output_path = provider_dir / filename
        output_path.write_text(content, encoding="utf-8")

        logger.info(f"Saved markdown to {output_path}")
        return output_path

    async def scrape_provider(
        self,
        provider_slug: str,
        save_to_disk: bool = True
    ) -> tuple[Optional[str], Optional[str]]:
        """Scrape the webpage for a specific insurance provider.

        Args:
            provider_slug: Provider slug (e.g., "goudse_expat_pakket")
            save_to_disk: Whether to save markdown file to disk

        Returns:
            Tuple of (url, markdown_content)
        """
        config = get_provider_config(provider_slug)

        if not config:
            logger.warning(f"No configuration found for provider: {provider_slug}")
            return None, None

        if not config.url:
            logger.warning(f"No URL configured for provider: {provider_slug}")
            return None, None

        markdown_content = await self.scrape_url(
            url=config.url,
            provider_name=config.provider_name,
        )

        if markdown_content and save_to_disk:
            self.save_markdown(
                content=markdown_content,
                provider_slug=config.provider_slug,
            )

        return config.url, markdown_content

    async def scrape_all_providers(self, save_to_disk: bool = True) -> dict[str, tuple[Optional[str], Optional[str]]]:
        """Scrape all configured insurance providers.

        Args:
            save_to_disk: Whether to save markdown files to disk

        Returns:
            Dict mapping provider_slug to (url, markdown_content) tuple
        """
        all_results = {}

        provider_slugs = get_all_provider_slugs()
        logger.info(f"Scraping {len(provider_slugs)} insurance providers")

        for provider_slug in provider_slugs:
            logger.info(f"Scraping provider: {provider_slug}")
            result = await self.scrape_provider(provider_slug, save_to_disk)
            all_results[provider_slug] = result

        logger.info(f"Completed scraping all providers")
        return all_results


# Convenience function for running scraper
async def scrape_insurance_data(
    provider_slug: Optional[str] = None,
    save_to_disk: bool = True
) -> dict:
    """Scrape insurance data (convenience function).

    Args:
        provider_slug: Optional provider slug to scrape (scrapes all if None)
        save_to_disk: Whether to save markdown files to disk

    Returns:
        Dict of scraping results
    """
    scraper = InsuranceScraper()

    if provider_slug:
        result = await scraper.scrape_provider(provider_slug, save_to_disk)
        return {provider_slug: result}
    else:
        return await scraper.scrape_all_providers(save_to_disk)
