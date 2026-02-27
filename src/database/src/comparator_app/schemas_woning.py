"""
Pydantic schemas for housing advice form (AdviesAanvraagWoning) validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, date


class AdviesAanvraagWoningInput(BaseModel):
    """
    Validated input data for creating an AdviesAanvraagWoning.
    """

    # Core identification
    external_result_id: str = Field(..., min_length=1, max_length=255)
    form_id: str = Field(..., max_length=50)
    email: EmailStr
    ingediend_op: datetime

    # Referral metadata
    referral_source: Optional[str] = Field(None, max_length=255)
    referral_medium: Optional[str] = Field(None, max_length=255)
    referral_campaign: Optional[str] = Field(None, max_length=500)

    # Gegevens aanvrager
    voornaam: Optional[str] = Field(None, max_length=255)
    achternaam: Optional[str] = Field(None, max_length=255)
    geboortedatum: Optional[date] = None
    geslacht: Optional[str] = Field(None, max_length=50)
    telefoonnummer: Optional[str] = Field(None, max_length=100)
    nationaliteit: Optional[str] = Field(None, max_length=255)
    woonland_buitenland: Optional[str] = Field(None, max_length=255)
    correspondentie_adres_nl: Optional[str] = Field(None, max_length=500)
    vertrekdatum: Optional[date] = None
    uitgeschreven_brp: Optional[str] = Field(None, max_length=255)

    # Gegevens woning
    woning_straat_huisnummer: Optional[str] = Field(None, max_length=500)
    woning_postcode_plaats: Optional[str] = Field(None, max_length=255)
    woning_land: Optional[str] = Field(None, max_length=255)
    woning_gebruik: Optional[str] = Field(None, max_length=500)
    woning_gebruik_extra: Optional[str] = None
    soort_woning: Optional[str] = Field(None, max_length=255)
    bouwaard: Optional[str] = Field(None, max_length=255)
    dakbedekking: Optional[str] = Field(None, max_length=255)
    bijzonderheden_woning: Optional[str] = None
    woning_extra_info: Optional[str] = None

    # Verzekeringen woning
    interesse_verzekeringen: Optional[str] = None
    gewenste_startdatum: Optional[str] = Field(None, max_length=255)

    # Verzekeringen buitenland
    interesse_internationale_verzekeringen: Optional[str] = None

    # Opmerkingen
    opmerkingen: Optional[str] = None

    # Raw backup
    raw_form_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('geboortedatum', 'vertrekdatum')
    @classmethod
    def validate_dates(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        import logging
        logger = logging.getLogger(__name__)
        if v.year < 1900:
            logger.warning(f'Date {v} seems invalid (before 1900) - keeping as-is')
        return v

    @field_validator('email')
    @classmethod
    def validate_email_not_test(cls, v: str) -> str:
        if any(test in v.lower() for test in ['test@', 'example@', 'noreply@']):
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Test/example email detected: {v}")
        return v
