"""
Factory for creating embedding models.

Supports multiple providers: OpenAI, Gemini, OpenRouter.
Uses LangChain's Embeddings interface for consistency.
"""

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr

from src.ingestion.config.settings import EmbeddingSettings
from src.config import OPENAI_API_KEY, GEMINI_API_KEY


class EmbedderFactory:
    """Factory for creating embedding models"""

    @staticmethod
    def create(settings: EmbeddingSettings, api_key: str = None) -> Embeddings:
        """
        Create an embeddings model based on settings.

        Args:
            settings: EmbeddingSettings configuration
            api_key: Optional API key (if not provided, tries to load from config)

        Returns:
            LangChain Embeddings instance

        Raises:
            ValueError: If provider is unknown or API key is missing
        """
        provider = settings.provider

        if provider == "openai":
            return EmbedderFactory._create_openai(settings, api_key)
        elif provider == "gemini":
            return EmbedderFactory._create_gemini(settings, api_key)
        elif provider == "openrouter":
            return EmbedderFactory._create_openrouter(settings, api_key)
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

    @staticmethod
    def _create_openai(settings: EmbeddingSettings, api_key: str = None) -> OpenAIEmbeddings:
        """Create OpenAI embeddings"""
        key = api_key or OPENAI_API_KEY
        if not key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env")

        return OpenAIEmbeddings(
            model=settings.model_name,
            api_key=SecretStr(key) if key else None
        )

    @staticmethod
    def _create_gemini(settings: EmbeddingSettings, api_key: str = None) -> GoogleGenerativeAIEmbeddings:
        """Create Google Gemini embeddings"""
        key = api_key or GEMINI_API_KEY
        if not key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in .env")

        return GoogleGenerativeAIEmbeddings(
            model=settings.model_name,
            google_api_key=SecretStr(key) if key else None
        )

    @staticmethod
    def _create_openrouter(settings: EmbeddingSettings, api_key: str = None) -> OpenAIEmbeddings:
        """
        Create OpenRouter embeddings.

        OpenRouter acts as a proxy for various embedding models,
        using OpenAI-compatible API format.
        """
        if not api_key:
            raise ValueError("OpenRouter API key not found. Provide api_key parameter")

        # OpenRouter uses OpenAI-compatible API
        return OpenAIEmbeddings(
            model=settings.model_name,
            openai_api_key=SecretStr(api_key),
            openai_api_base=settings.openrouter_base_url
        )

    @staticmethod
    def get_embedding_dimension(settings: EmbeddingSettings) -> int:
        """
        Get embedding dimension for a given configuration.

        Args:
            settings: EmbeddingSettings configuration

        Returns:
            Embedding dimension
        """
        return settings.dimension
