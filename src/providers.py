"""Global provider registry — single source of truth for all insurance providers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Provider:
    """Insurance provider metadata.

    Args:
        folder: Actual folder name in data/documents/.
        display_name: Human-readable name.
        billing_period: "monthly" or "yearly".
        region_column: Column name in regio_mapping.xlsx (None if not mapped).
    """

    folder: str
    display_name: str
    billing_period: str
    region_column: str | None


PROVIDERS: dict[str, Provider] = {
    "oom_wib": Provider("oom_wib", "OOM WIB", "monthly", "WIB"),
    "oom_tib": Provider("oom_tib", "OOM TIB", "monthly", "TIB"),
    "goudse_expat_pakket": Provider("goudse_expat_pakket", "Goudse Expat Package", "yearly", "GEP"),
    "goudse_ngo_zendelingen": Provider("goudse_ngo_zendelingen", "Goudse NGO Zendelingen", "yearly", "NGO"),
    "goudse_working_nomad": Provider("goudse_working_nomad", "Goudse Working Nomad", "monthly", "Goudse_WN"),
    "allianz_globetrotter": Provider("allianz_globetrotter", "Allianz Globetrotter", "monthly", None),
    "allianz_care": Provider("allianz_care", "Allianz Care", "yearly", "Allianz_Health"),
    "globality_yougenio": Provider("globality_yougenio", "Globality Yougenio", "monthly", "Globality"),
    "expatriate_group": Provider("expatriate_group", "Expatriate Group", "monthly", "TEG_Health"),
    "cigna_global_care": Provider("cigna_global_care", "Cigna Global Care", "yearly", "Cigna_Global"),
    "cigna_close_care": Provider("cigna_close_care", "Cigna Close Care", "yearly", "Cigna_Close_Care"),
    "special_isis": Provider("special_isis", "Special ISIS", "monthly", "Special_ISIS"),
    "International Expat Insurance": Provider("International Expat Insurance", "International Expat Insurance", "monthly", "IEI"),
    "ACS": Provider("ACS", "ACS International", "yearly", None),
    "IMG_": Provider("IMG_", "IMG International Medical Group", "yearly", None),
    "MSH": Provider("MSH", "MSH International", "yearly", None),
}

# Convenience lookups
ALL_PROVIDER_NAMES: list[str] = list(PROVIDERS.keys())

FOLDER_TO_PROVIDER: dict[str, str] = {p.folder: name for name, p in PROVIDERS.items()}

REGION_COLUMN_TO_PROVIDER: dict[str, str] = {
    p.region_column: name for name, p in PROVIDERS.items() if p.region_column
}
