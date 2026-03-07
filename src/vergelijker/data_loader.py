"""
data_loader.py

Utility functions for loading insurance premium data from an Excel workbook.

Workbook layout
---------------
* Sheet **"vertaling"**
  - Columns: ``AFK`` (ISO code), ``LAND`` (NL), ``COUNTRY`` (EN), then one column
    per **company sheet ID**. These IDs are short aliases (max 31 chars) that map
    to user‑friendly company names via ``COMPANY_NAME_MAP`` below.
* One **additional sheet per company** (sheet name = short ID)
  - The first three rows form a MultiIndex header:
      0. *regio*         (e.g. "A", "B", "C", ...)
      1. *dekking*       ("Budget", "Medium", "Top", ...)
      2. *eigen risico*  (0, 250, 500, 1000, 2500)
  - The first column holds the **age** (0 – 100). All other cells are premium
    values that may include euro‑signs and use commas as decimal separator.

This module loads those sheets, cleans the data, and always exposes **the full
company display names** to the rest of the backend / frontend.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Union

import pandas as pd
# ---------------------------------------------------------------------------
# Company name mapping
# ---------------------------------------------------------------------------

#: Map **sheet IDs** (short names used in Excel) → **full display names**
COMPANY_NAME_MAP: Dict[str, str] = {
    # Dataset ziektekostenverzekeringen
    "GEP": "Goudse Expat Pakket",
    "WIB": "OOM Wonen in het buitenland",
    "NGO": "Goudse NGO/Zendelingen Pakket",
    "IEI": "International Expat Insurance",
    "Allianz_Health": "Allianz Healthcare",
    "Globality": "Globality Yougenio",
    "TEG_Health": "The Expatriate Group Health insurance",
    "Cigna_Global" : "Cigna Global",
    "Cigna_Close_Care" : "Cigna Close Care",
    "April" : "April MyHealth",
    # Dataset reisverzekeringen
    "Special_Isis": "Special ISIS - all-in",
    "Working_Nomad": "Goudse Working Nomad",
    "Globetrotter": "Allianz Globetrotter",
    "TIB": "OOM Tijdelijk in het Buitenland",
    "Safetywing_Nomad": "Safetywing Nomad Insurances",
}

# Helper: inverse map if ever needed (display → sheet id)
DISPLAY_TO_SHEET = {v: k for k, v in COMPANY_NAME_MAP.items()}



# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _clean_premium_df(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a raw premium table.

    * Drops empty rows/columns.
    * Converts the index (age) to ``int``.
    * Removes euro symbols, converts comma decimals to dots, and casts values
      to ``float`` (except for "website" which is preserved as string).
    * Normalises the MultiIndex columns: ``(regio, dekking, eigen_risico:int)``.
    """
    # Remove completely empty rows / columns
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")

    # Ensure the index represents age as integers
    df.index = pd.to_numeric(df.index, errors="coerce")
    df = df.loc[df.index.notna()]
    df.index = df.index.astype(int)

    # Strip euro symbols and change comma decimal → dot
    df = df.replace({"€": "", ",": "."}, regex=True)

    # Handle numeric conversion while preserving "website" values
    def convert_cell(cell):
        if pd.isna(cell):
            return cell
        if isinstance(cell, str):
            cell_lower = cell.lower().strip()
            if cell_lower in ["website", "www", "Website", "WEBSITE"]:
                return "website"
            elif cell_lower in ["nvt", "n.v.t.", "NVT", "N.V.T.", "Nvt", "Nvt.", "geen acceptatie"]:
                return cell  # Keep NVT as is
        # Try to convert to numeric, return original if it fails
        try:
            return round(float(cell), 2)
        except (ValueError, TypeError):
            return cell
    
    # Apply the conversion function to all cells
    df = df.map(convert_cell)

    # Normalise column levels (eigen risico → int where possible)
    new_cols = []
    for regio, dekking, risico in df.columns:
        try:
            risico = int(float(risico))
        except (TypeError, ValueError):
            pass  # leave as‑is if conversion fails
        new_cols.append((
            str(regio).strip().strip('\u200b\ufeff'),  # Remove zero-width space and BOM
            str(dekking).strip().strip('\u200b\ufeff'), 
            risico
        ))
    df.columns = pd.MultiIndex.from_tuples(
        new_cols, names=["regio", "dekking", "eigen_risico"]
    )
    return df

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def load_region_mapping(excel_path: str | Path) -> Dict[str, Dict[str, Union[str, int]]]:
    """
    Return ``{display_name: {LAND: regio}}`` mapping for every company.
    
    This version correctly handles both string and integer data in region columns.
    """
    excel_path = Path(excel_path)
    df = pd.read_excel(excel_path, sheet_name="vertaling")
    mapping: Dict[str, Dict[str, Union[str, int]]] = {}
    
    for sheet_id in df.columns[1:]:  # columns after LAND are companies (sheet IDs)
        if sheet_id.startswith('Unnamed:'):  # Skip unnamed columns
            continue
            
        display_name = COMPANY_NAME_MAP.get(sheet_id, sheet_id)
        
        # Apply a function to handle mixed types: strip strings, leave integers.
        # .fillna('') handles any empty cells from Excel.
        regions = df[sheet_id].apply(lambda x: x.strip() if isinstance(x, str) else x).fillna('')
        
        mapping[display_name] = dict(zip(df["LAND"].str.strip(), regions))
        
    return mapping


@lru_cache(maxsize=None)
def load_company_sheet(excel_path: str | Path, sheet_id: str) -> pd.DataFrame:
    """Load and clean the premium table for one insurance company (by sheet ID)."""
    excel_path = Path(excel_path)
    df_raw = pd.read_excel(
        excel_path,
        sheet_name=sheet_id,
        header=[0, 1, 2],
        index_col=0,  # first column is age
        decimal=",",  # Dutch comma decimal
        engine="openpyxl",
    )
    return _clean_premium_df(df_raw)


@lru_cache(maxsize=None)
def load_all_company_data(excel_path: str | Path) -> Dict[str, pd.DataFrame]:
    """Load and clean all company sheets and return keyed by *display names*."""
    excel_path = Path(excel_path)
    xl = pd.ExcelFile(excel_path, engine="openpyxl")
    data: Dict[str, pd.DataFrame] = {}
    for sheet_id in xl.sheet_names:
        if sheet_id.lower() == "vertaling":
            continue
        display_name = COMPANY_NAME_MAP.get(sheet_id, sheet_id)
        data[display_name] = load_company_sheet(excel_path, sheet_id)
    return data


__all__ = [
    "COMPANY_NAME_MAP",
    "load_region_mapping",
    "load_company_sheet",
    "load_all_company_data",
]