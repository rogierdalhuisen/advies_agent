"""JSON cache for preprocessed user data."""

import json
from pathlib import Path
from typing import TYPE_CHECKING

from src.config import DATA_DIR

if TYPE_CHECKING:
    from .preprocessor import PreprocessedUser

CACHE_DIR = DATA_DIR / "preprocessed"


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_from_cache(aanvraag_id: int) -> "PreprocessedUser | None":
    """Load a cached PreprocessedUser from disk.

    Args:
        aanvraag_id: The request ID to look up.

    Returns:
        PreprocessedUser if cache hit, None otherwise.
    """
    from .preprocessor import PreprocessedUser

    path = CACHE_DIR / f"{aanvraag_id}.json"
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return PreprocessedUser(**data)


def save_to_cache(user: "PreprocessedUser") -> None:
    """Persist a PreprocessedUser to the JSON cache.

    Args:
        user: The preprocessed user to cache.
    """
    from dataclasses import asdict
    from datetime import date

    _ensure_cache_dir()
    path = CACHE_DIR / f"{user.aanvraag_id}.json"

    data = asdict(user)
    # Remove _raw (not serializable / not needed in cache)
    data.pop("_raw", None)
    # Convert date objects to ISO strings
    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.isoformat()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
