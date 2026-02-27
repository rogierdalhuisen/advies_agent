"""
Pydantic schemas for English advice form (AdviesAanvraagEngels) validation.

Validates incoming data before it touches the database.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, date


class AdviesAanvraagEngelsInput(BaseModel):
    """
    Validated input data for creating an AdviesAanvraagEngels.

    Cleaned, validated data extracted from an English form submission,
    ready for database insertion.
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

    # Personal data
    advies_voor_mezelf: Optional[str] = Field(None, max_length=255)
    aanhef: Optional[str] = Field(None, max_length=50)
    voorletters_roepnaam: Optional[str] = Field(None, max_length=255)
    achternaam: Optional[str] = Field(None, max_length=255)
    geboortedatum: Optional[date] = None
    land_nationaliteit: Optional[str] = Field(None, max_length=255)
    telefoonnummer: Optional[str] = Field(None, max_length=100)
    vaste_woonplaats: Optional[str] = Field(None, max_length=500)

    # Multiple insured persons
    meerdere_verzekerden: Optional[str] = None

    # Abroad / Situation
    bestemming_land: Optional[str] = Field(None, max_length=255)
    verwachte_duur_verblijf: Optional[str] = Field(None, max_length=255)
    vertrekdatum: Optional[date] = None
    vertrek_wanneer: Optional[date] = None
    verwachte_vertrekdatum: Optional[date] = None
    hoofdreden_verblijf: Optional[str] = Field(None, max_length=500)

    # Work
    werk_omschrijving: Optional[str] = None
    plannen_omschrijving: Optional[str] = None

    # Income protection insurance (AOV)
    interesse_aov: Optional[str] = Field(None, max_length=255)
    loondienst_of_zelfstandig: Optional[str] = Field(None, max_length=255)
    bruto_jaarinkomen: Optional[str] = Field(None, max_length=255)
    bruto_salaris_inkomen: Optional[str] = Field(None, max_length=255)

    # Health insurance
    interesse_zkv: Optional[str] = Field(None, max_length=255)
    zkv_periode: Optional[str] = Field(None, max_length=255)
    zkv_periode_omschrijving_motivatie: Optional[str] = None
    zkv_periode_omschrijving: Optional[str] = None
    huidige_verzekeraar: Optional[str] = Field(None, max_length=255)
    voorkeur_verzekeraar: Optional[str] = Field(None, max_length=255)
    medische_bijzonderheden: Optional[str] = Field(None, max_length=255)
    medische_bijzonderheden_toelichting: Optional[str] = None
    specifieke_wensen_zkv: Optional[str] = Field(None, max_length=255)
    wensen_toelichting: Optional[str] = None
    dekking_zwangerschap: Optional[str] = Field(None, max_length=255)
    zwangerschap_toelichting: Optional[str] = None

    # Additional insurances
    andere_verzekeringen_interesse: Optional[str] = None

    # Remarks
    opmerkingen: Optional[str] = None

    # Raw backup
    raw_form_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('geboortedatum', 'vertrekdatum', 'vertrek_wanneer', 'verwachte_vertrekdatum')
    @classmethod
    def validate_dates(cls, v: Optional[date]) -> Optional[date]:
        """Validate dates - log warnings for suspicious data but keep it."""
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
        """Warn about test emails but allow them."""
        if any(test in v.lower() for test in ['test@', 'example@', 'noreply@']):
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Test/example email detected: {v}")
        return v
