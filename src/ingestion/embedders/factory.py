"""
Factory for creating embedding models.

Simplified to use OpenRouter as central hub, with direct OpenAI/Gemini as fallback.
"""

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr
import os

from src.ingestion.config.settings import EmbeddingSettings
from src.config import OPENAI_API_KEY, GEMINI_API_KEY


class EmbedderFactory:
    """Factory for creating embedding models"""

    @staticmethod
    def create(settings: EmbeddingSettings) -> Embeddings:
        """
        Create an embeddings model based on settings.

        Args:
            settings: EmbeddingSettings configuration

        Returns:
            LangChain Embeddings instance

        Raises:
            ValueError: If provider is unknown or API key is missing
        """
        provider = settings.provider

        if provider == "openrouter":
            return EmbedderFactory._create_openrouter(settings)
        elif provider == "openai":
            return EmbedderFactory._create_openai(settings)
        elif provider == "gemini":
            return EmbedderFactory._create_gemini(settings)
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

    @staticmethod
    def _create_openrouter(settings: EmbeddingSettings) -> OpenAIEmbeddings:
        """
        Create OpenRouter embeddings (recommended).

        OpenRouter acts as a universal proxy for all embedding models.
        Use model names like: openai/text-embedding-3-large, google/text-embedding-004, etc.
        """
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY in .env")

        return OpenAIEmbeddings(
            model=settings.model_name,
            openai_api_key=SecretStr(key),
            openai_api_base=settings.openrouter_base_url
        )

    @staticmethod
    def _create_openai(settings: EmbeddingSettings) -> OpenAIEmbeddings:
        """Create direct OpenAI embeddings (fallback)"""
        key = OPENAI_API_KEY
        if not key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env")

        return OpenAIEmbeddings(
            model=settings.model_name,
            api_key=SecretStr(key)
        )

    @staticmethod
    def _create_gemini(settings: EmbeddingSettings) -> GoogleGenerativeAIEmbeddings:
        """Create direct Gemini embeddings (fallback)"""
        key = GEMINI_API_KEY
        if not key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in .env")

        return GoogleGenerativeAIEmbeddings(
            model=settings.model_name,
            google_api_key=SecretStr(key)
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
