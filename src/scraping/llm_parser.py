"""LLM-based HTML to Markdown parser using Gemini Flash.

This module uses an LLM to extract clean markdown content from scraped HTML pages.
The advantage of using an LLM is that it's robust to page structure changes and
can intelligently extract the main content while filtering out navigation, ads, etc.
"""

import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


class LLMContentParser:
    """Parse HTML content to clean markdown using Gemini Flash."""

    SYSTEM_PROMPT = """You are an expert at extracting clean, structured content from HTML pages.

Your task is to:
1. Extract ONLY the main content from the HTML (ignore navigation, footers, ads, cookie banners, etc.)
2. Convert the content to clean, well-formatted Markdown
3. Preserve the document structure (headings, lists, tables, etc.)
4. Keep all important information like coverage details, premiums, conditions, benefits
5. write it optimized for embedding-retrieval performance and translate it to english
5. Remove any marketing fluff or irrelevant content
6. DO NOT include links to other pages or documents - only extract text content
7. If there are tables with premium information or coverage details, preserve them in markdown table format

Return ONLY the markdown content, without any preamble or explanation.
"""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """Initialize the LLM parser.

        Args:
            model_name: Gemini model to use (default: gemini-2.0-flash-exp for speed and cost)
        """
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=GEMINI_API_KEY,
            temperature=0,  # Deterministic output
            max_tokens=8000,  # Allow for large documents
        )

        logger.info(f"Initialized LLM parser with model: {model_name}")

    def parse_html_to_markdown(self, html_content: str, url: str) -> Optional[str]:
        """Parse HTML content to clean markdown using the LLM.

        Args:
            html_content: Raw HTML content from the scraped page
            url: URL of the page (for logging/context)

        Returns:
            Clean markdown content, or None if parsing failed
        """
        try:
            logger.info(f"Parsing HTML from {url} (length: {len(html_content)} chars)")

            # Truncate if too long (Gemini Flash has limits)
            max_html_length = 100_000  # ~100k chars
            if len(html_content) > max_html_length:
                logger.warning(f"HTML content too long ({len(html_content)} chars), truncating to {max_html_length}")
                html_content = html_content[:max_html_length]

            # Create messages
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=f"Extract clean markdown from this HTML page:\n\n{html_content}")
            ]

            # Get LLM response
            response = self.llm.invoke(messages)
            markdown_content = response.content.strip()

            if not markdown_content:
                logger.error(f"LLM returned empty content for {url}")
                return None

            logger.info(f"Successfully parsed {url} to markdown ({len(markdown_content)} chars)")
            return markdown_content

        except Exception as e:
            logger.error(f"Error parsing HTML from {url}: {e}", exc_info=True)
            return None

    def parse_with_context(
        self,
        html_content: str,
        url: str,
        provider_name: str,
        document_type: str
    ) -> Optional[str]:
        """Parse HTML with additional context about the insurance provider.

        This can help the LLM better understand what content to extract.

        Args:
            html_content: Raw HTML content
            url: URL of the page
            provider_name: Name of insurance provider (e.g., "Goudse Expat Pakket")
            document_type: Type of document (e.g., "coverage", "premiums", "conditions")

        Returns:
            Clean markdown content, or None if parsing failed
        """
        try:
            logger.info(f"Parsing {document_type} page from {provider_name}")

            # Enhanced prompt with context
            context_prompt = f"""Extract clean markdown from this {document_type} page for {provider_name}.

Focus on extracting:
- Coverage details and benefits
- Premium information and pricing tables
- Policy conditions and terms
- Deductibles and limits
- Exclusions and waiting periods

Ignore navigation, footers, cookie banners, and marketing content.

HTML content:
{html_content}"""

            # Truncate if needed
            max_html_length = 100_000
            if len(context_prompt) > max_html_length:
                logger.warning(f"Content too long, truncating")
                excess = len(context_prompt) - max_html_length
                html_content = html_content[:len(html_content) - excess]
                context_prompt = f"""Extract clean markdown from this {document_type} page for {provider_name}.

Focus on extracting coverage details, benefits, premiums, conditions, and policy terms.

HTML content:
{html_content}"""

            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=context_prompt)
            ]

            response = self.llm.invoke(messages)
            markdown_content = response.content.strip()

            if not markdown_content:
                logger.error(f"LLM returned empty content for {provider_name} - {document_type}")
                return None

            logger.info(f"Successfully parsed {provider_name} {document_type} ({len(markdown_content)} chars)")
            return markdown_content

        except Exception as e:
            logger.error(f"Error parsing {provider_name} - {document_type}: {e}", exc_info=True)
            return None
