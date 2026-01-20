"""Configuration for insurance company webpage URLs.

This file contains the URLs for each insurance provider's main documentation page
that needs to be scraped monthly to keep the knowledge base up-to-date.

Each insurance provider has ONE webpage URL that will be scraped.
"""

from typing import Dict, Optional
from pydantic import BaseModel


class InsuranceURLConfig(BaseModel):
    """Configuration for a single insurance provider."""
    provider_name: str
    provider_slug: str  # e.g., "goudse_expat_pakket"
    url: Optional[str] = None  # Single URL to scrape for this provider
    description: str = ""  # Optional description


# Configuration for all insurance providers
# TODO: Fill in actual URL for each provider
INSURANCE_URLS: Dict[str, InsuranceURLConfig] = {
    "goudse_expat_pakket": InsuranceURLConfig(
        provider_name="Goudse Expat Pakket",
        provider_slug="goudse_expat_pakket",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/de-goudse-verzekeringen/goudse-expat-pakket/",
        description="Goudse expat insurance package"
    ),

    "goudse_ngo_zendelingen": InsuranceURLConfig(
        provider_name="Goudse NGO Zendelingen",
        provider_slug="goudse_ngo_zendelingen",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/de-goudse-verzekeringen/ngo/",  # TODO: Add actual URL
        description="NGO and missionary insurance coverage"
    ),

    "goudse_working_nomad": InsuranceURLConfig(
        provider_name="Goudse Working Nomad",
        provider_slug="goudse_working_nomad",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/de-goudse-verzekeringen/isis-working-nomad-reisverzekering/",  # TODO: Add actual URL
        description="Working nomad insurance"
    ),

    "allianz_care": InsuranceURLConfig(
        provider_name="Allianz Care",
        provider_slug="allianz_care",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/allianz-care/international-health-insurance/",  # TODO: Add actual URL
        description="Allianz international health insurance"
    ),

    "allianz_globetrotter": InsuranceURLConfig(
        provider_name="Allianz Globetrotter",
        provider_slug="allianz_globetrotter",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/allianz-global-assistance/globetrotter-reisverzekering/",  
        description="Allianz travel insurance"
    ),

    "cigna_close_care": InsuranceURLConfig(
        provider_name="Cigna Close Care",
        provider_slug="cigna_close_care",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/cigna/cigna-close-care/",  
        description="Cigna Close Care plan"
    ),

    "cigna_global_care": InsuranceURLConfig(
        provider_name="Cigna Global Care",
        provider_slug="cigna_global_care",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/cigna/cigna-global-health/",  
        description="Cigna Global Care plan"
    ),

    "expatriate_group": InsuranceURLConfig(
        provider_name="Expatriate Group",
        provider_slug="expatriate_group",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/expatriate-group/long-term-international-health-insurance/",  
        description="Expatriate Group insurance"
    ),

    "globality_yougenio": InsuranceURLConfig(
        provider_name="Globality YouGenio",
        provider_slug="globality_yougenio",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/globality-health/globality-health-insurance/",  
        description="Globality YouGenio health insurance"
    ),

    "oom_tib": InsuranceURLConfig(
        provider_name="OOM TIB",
        provider_slug="oom_tib",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/oom-verzekeringen/oom-tijdelijk-buitenland/",  
        description="OOM Temporary Insurance Abroad"
    ),

    "oom_wib": InsuranceURLConfig(
        provider_name="OOM WIB",
        provider_slug="oom_wib",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/oom-verzekeringen/oom-wonen-in-het-buitenland/",  
        description="OOM International Insurance Abroad"
    ),

    "special_isis": InsuranceURLConfig(
        provider_name="Special ISIS",
        provider_slug="special_isis",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/de-goudse-verzekeringen/special-isis-reisverzekering/",  
        description="Special ISIS insurance"
    ),

    "ACS": InsuranceURLConfig(
        provider_name="ACS",
        provider_slug="ACS",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/acs/globe-traveller/",  
        description="ACS international insurance"
    ),

    "IMG_": InsuranceURLConfig(
        provider_name="IMG",
        provider_slug="IMG_",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/IMG/ziektekostenverzekering---global-prima-medical-insurance--gpmi-/",  
        description="IMG international insurance"
    ),

    "International Expat Insurance": InsuranceURLConfig(
        provider_name="International Expat Insurance",
        provider_slug="International Expat Insurance",
        url="https://www.expatverzekering.nl/internationale-verzekeringen/verzekeraars/henner/international-expat-insurance/",  
        description="International Expat Insurance"
    ),

    "MSH": InsuranceURLConfig(
        provider_name="MSH",
        provider_slug="MSH",
        url=None,  # TODO: Add actual URL
        description="MSH international insurance"
    ),
}


def get_all_configs() -> list[InsuranceURLConfig]:
    """Get all insurance configurations as a list."""
    return list(INSURANCE_URLS.values())


def get_provider_config(provider_slug: str) -> Optional[InsuranceURLConfig]:
    """Get configuration for a specific insurance provider."""
    return INSURANCE_URLS.get(provider_slug)


def get_all_provider_slugs() -> list[str]:
    """Get list of all provider slugs."""
    return list(INSURANCE_URLS.keys())
