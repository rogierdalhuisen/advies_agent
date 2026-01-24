#!/usr/bin/env python3
"""Extract AdviesAanvragen data to JSON.

Usage:
    uv run python scripts/load_aanvragen.py --all
    uv run python scripts/load_aanvragen.py --recent
    uv run python scripts/load_aanvragen.py --email user@example.com

To change which fields are extracted, edit EXTRACT_POSITIONS in:
    src/database/repository.py
"""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("POSTGRES_HOST", "localhost")

from src.database import get_all, get_recent_24h, get_by_email

OUTPUT_FILE = PROJECT_ROOT / "data" / "user_data" / "user_data.json"


def serialize(obj):
    """JSON serializer for dates/datetimes."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return str(obj)


def clean_row(row: dict) -> dict:
    """Clean row: serialize dates, keep all fields (null if empty)."""
    return {k: serialize(v) if isinstance(v, (date, datetime)) else v
            for k, v in row.items()}


def load_existing() -> dict:
    """Load existing data from JSON file."""
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            return {item["aanvraag_id"]: item for item in json.load(f)}
    return {}


def save_data(data: dict):
    """Save data to JSON file."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(list(data.values()), f, indent=2, ensure_ascii=False)


def extract_and_save(rows: list[dict]) -> int:
    """Extract and merge with existing data."""
    existing = load_existing()
    for row in rows:
        cleaned = clean_row(row)
        existing[cleaned["aanvraag_id"]] = cleaned
    save_data(existing)
    return len(rows)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  --all           Extract all aanvragen")
        print("  --recent        Extract last 24 hours")
        print("  --email EMAIL   Extract by email")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--all":
        count = extract_and_save(get_all())
        print(f"Extracted {count} aanvragen (all)")
    elif arg == "--recent":
        count = extract_and_save(get_recent_24h())
        print(f"Extracted {count} aanvragen (last 24h)")
    elif arg == "--email" and len(sys.argv) > 2:
        count = extract_and_save(get_by_email(sys.argv[2]))
        print(f"Extracted {count} aanvragen for {sys.argv[2]}")
    else:
        print("Invalid arguments")
        sys.exit(1)

    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
