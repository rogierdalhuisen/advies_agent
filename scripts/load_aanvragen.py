#!/usr/bin/env python3
"""Simple script to load AdviesAanvragen data.

Usage:
    # Run directly to see stats and recent aanvragen
    uv run python scripts/load_aanvragen.py

    # Import in Python/Jupyter for interactive use
    from scripts.load_aanvragen import get_by_id, get_recent, search

    user = get_by_id(42)
    print(user.full_name, user.to_context_dict())
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("POSTGRES_HOST", "localhost")  # For local dev

from src.database import AdviesAanvragenRepository, AdviesAanvraag


def get_repo() -> AdviesAanvragenRepository:
    """Get repository instance."""
    return AdviesAanvragenRepository()


def get_by_id(aanvraag_id: int) -> AdviesAanvraag | None:
    """Load a single aanvraag by ID."""
    return get_repo().get_by_id(aanvraag_id)


def get_by_email(email: str) -> list[AdviesAanvraag]:
    """Load all aanvragen for an email address."""
    return get_repo().get_by_email(email)


def get_recent(limit: int = 10) -> list[AdviesAanvraag]:
    """Load most recent aanvragen."""
    return get_repo().get_recent(limit)


def search(
    destination: str = None,
    zkv: bool = None,
    aov: bool = None,
    limit: int = 10
) -> list[AdviesAanvraag]:
    """Search aanvragen with filters.

    Args:
        destination: Filter by country (partial match)
        zkv: Filter by health insurance interest (True/False)
        aov: Filter by disability insurance interest (True/False)
        limit: Max results to return
    """
    return get_repo().search(
        destination=destination,
        interested_zkv=zkv,
        interested_aov=aov,
        limit=limit
    )


def stats() -> dict:
    """Get database statistics."""
    return get_repo().get_statistics()


def print_aanvraag(a: AdviesAanvraag, verbose: bool = False):
    """Pretty print an aanvraag."""
    print(f"[{a.aanvraag_id}] {a.full_name}")
    print(f"    Destination: {a.destination}")
    print(f"    ZKV: {a.wants_health_insurance}, AOV: {a.wants_disability_insurance}")
    if verbose:
        print(f"    Email: {a.email}")
        print(f"    Family: {len(a.family_members)} members")
        if a.zkv_dekkingsvariant:
            print(f"    Coverage: {a.zkv_dekkingsvariant}")


# Quick usage when run directly
if __name__ == "__main__":
    print("=== Database Stats ===")
    s = stats()
    print(f"Total requests: {s['total_requests']}")
    print(f"ZKV interested: {s['zkv_interested']}")
    print(f"Unique destinations: {s['unique_destinations']}")

    print("\n=== Recent 5 Aanvragen ===")
    for a in get_recent(5):
        print_aanvraag(a)
        print()
