"""Preprocessing module that transforms a PreprocessedUser into orchestrator inputs."""

from dataclasses import fields

from src.database.data_preprocessor import PreprocessedUser
from .config import load_product_descriptions

# Fields that are passed separately or should not be in user_profile
_EXCLUDE_FROM_PROFILE = {"premiums", "_raw"}


def prepare_orchestrator_input(preprocessed_user: PreprocessedUser) -> dict:
    """Transform a PreprocessedUser into the four inputs expected by the hierarchical orchestrator.

    Args:
        preprocessed_user: A fully preprocessed user with calculated premiums.

    Returns:
        Dict with keys: user_profile, premiums, available_providers, product_descriptions.
    """
    # 1. Build user_profile: all dataclass fields except premiums and _raw, stripping None values
    user_profile = {}
    for f in fields(preprocessed_user):
        if f.name in _EXCLUDE_FROM_PROFILE:
            continue
        value = getattr(preprocessed_user, f.name)
        if value is None:
            continue
        # Convert date to string for JSON serialization
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        user_profile[f.name] = value

    # 2. Premiums are already in the right format: provider -> coverage_level -> {total, deductible, per_person}
    premiums = preprocessed_user.premiums

    # 3. Available providers = providers that have calculated premiums
    available_providers = list(premiums.keys())

    # 4. Product descriptions filtered to only available providers
    all_descriptions = load_product_descriptions()
    product_descriptions = {
        provider: all_descriptions[provider]
        for provider in available_providers
        if provider in all_descriptions
    }

    return {
        "user_profile": user_profile,
        "premiums": premiums,
        "available_providers": available_providers,
        "product_descriptions": product_descriptions,
    }
