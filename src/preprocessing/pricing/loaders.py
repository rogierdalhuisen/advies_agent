"""Data loaders for premium calculation."""

import json
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import DATA_DIR, DOCUMENTS_DIR
from src.providers import PROVIDERS


# Build column-to-folder and folder-to-column mappings from the providers registry
INSURANCE_COLUMN_TO_FOLDER: dict[str, str] = {
    p.region_column: name
    for name, p in PROVIDERS.items()
    if p.region_column
}

FOLDER_TO_INSURANCE_COLUMN: dict[str, str] = {v: k for k, v in INSURANCE_COLUMN_TO_FOLDER.items()}


def parse_premium_value(value: str | float | None) -> Optional[float]:
    """Parse premium values from various formats to float.

    Handles formats like:
    - "1.375,-" (Dutch format)
    - "123,32" (European decimal)
    - "€25,25"
    - 123.45 (already float)
    - null/None
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    # Remove currency symbols and whitespace
    cleaned = str(value).strip()
    cleaned = re.sub(r'[€$\s]', '', cleaned)

    # Handle "1.375,-" format (Dutch: dot as thousand separator, ends with ,-)
    if cleaned.endswith(',-'):
        cleaned = cleaned[:-2]  # Remove ,-
        cleaned = cleaned.replace('.', '')  # Remove thousand separator
        return float(cleaned)

    # Handle "1.000" as thousand (Dutch) vs "123,45" as decimal
    # If contains both . and , -> . is thousand, , is decimal
    if '.' in cleaned and ',' in cleaned:
        cleaned = cleaned.replace('.', '')  # Remove thousand separator
        cleaned = cleaned.replace(',', '.')  # Convert decimal separator
    elif ',' in cleaned:
        # Only comma -> it's the decimal separator
        cleaned = cleaned.replace(',', '.')
    # If only dot and looks like thousand (e.g., "1.000")
    elif '.' in cleaned:
        parts = cleaned.split('.')
        if len(parts) == 2 and len(parts[1]) == 3:
            # Likely thousand separator (e.g., "1.000")
            cleaned = cleaned.replace('.', '')

    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_deductible_value(value: str | float | int | None) -> Optional[float]:
    """Parse deductible values to float."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    # Remove currency symbols, spaces, and common text
    cleaned = str(value).strip()
    cleaned = re.sub(r'[€$\s]', '', cleaned)
    cleaned = cleaned.replace('.', '')  # Remove thousand separator
    cleaned = cleaned.replace(',', '.')  # Convert decimal separator

    try:
        return float(cleaned)
    except ValueError:
        return None


def load_region_mapping() -> pd.DataFrame:
    """Load the region mapping Excel file."""
    mapping_path = DATA_DIR / "regio_mapping.xlsx"
    if not mapping_path.exists():
        raise FileNotFoundError(f"Region mapping not found at {mapping_path}")

    df = pd.read_excel(mapping_path)
    # Normalize country names to lowercase for matching
    df['LAND_LOWER'] = df['LAND'].str.lower().str.strip()
    return df


def get_region_for_country(
    country: str,
    insurance_column: str,
    region_df: Optional[pd.DataFrame] = None
) -> Optional[str]:
    """Get the region code for a country and insurance.

    Args:
        country: Country name (in Dutch).
        insurance_column: Column name in region mapping (e.g., "GEP", "WIB").
        region_df: Pre-loaded region DataFrame (optional).

    Returns:
        Region code or None if not found.
    """
    if region_df is None:
        region_df = load_region_mapping()

    country_lower = country.lower().strip()
    match = region_df[region_df['LAND_LOWER'] == country_lower]

    if match.empty:
        return None

    if insurance_column not in region_df.columns:
        return None

    return match[insurance_column].iloc[0]


def load_premium_data(insurance_folder: str) -> Optional[list[dict]]:
    """Load premium data for an insurance provider.

    Args:
        insurance_folder: Folder name under data/documents/.

    Returns:
        List of premium records or None if no premiums file exists.
    """
    premium_path = DOCUMENTS_DIR / insurance_folder / "premiums.json"

    if not premium_path.exists():
        return None

    with open(premium_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def get_all_insurance_folders() -> list[str]:
    """Get list of all insurance folders that have premium files."""
    folders = []
    for folder in DOCUMENTS_DIR.iterdir():
        if folder.is_dir() and (folder / "premiums.json").exists():
            folders.append(folder.name)
    return folders


DEFAULT_DEDUCTIBLE = 500.0


def parse_user_deductible(user_record: dict) -> float:
    """Parse the user's preferred deductible from form data.

    Checks zkv_eigen_risico_voorkeur first, then zkv_eigen_risico_bedrag.
    Falls back to DEFAULT_DEDUCTIBLE (500) if neither is set.
    """
    # First check the dropdown preference
    pref = user_record.get('zkv_eigen_risico_voorkeur')
    if pref:
        parsed = parse_deductible_value(pref)
        if parsed is not None:
            return parsed

    # Then check custom amount
    custom = user_record.get('zkv_eigen_risico_bedrag')
    if custom:
        parsed = parse_deductible_value(custom)
        if parsed is not None:
            return parsed

    return DEFAULT_DEDUCTIBLE
