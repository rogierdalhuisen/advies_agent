"""
Pydantic schemas for OfferteArbeidsOngeschiktheid validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, date


class OfferteArbeidsOngeschiktheidInput(BaseModel):
    """
    Validated input data for creating an OfferteArbeidsOngeschiktheid.
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
    geslacht: Optional[str] = Field(None, max_length=50)
    achternaam: Optional[str] = Field(None, max_length=255)
    voorletters: Optional[str] = Field(None, max_length=255)
    geboortedatum: Optional[date] = None
    telefoonnummer: Optional[str] = Field(None, max_length=100)
    nationaliteit: Optional[str] = Field(None, max_length=255)

    # Destination and departure
    bestemming_land: Optional[str] = Field(None, max_length=255)
    vertrekdatum: Optional[date] = None
    vertrek_wanneer: Optional[date] = None
    verwachte_vertrekdatum: Optional[date] = None
    verwachte_duur_verblijf: Optional[str] = Field(None, max_length=255)

    # Work and income
    bruto_jaarinkomen: Optional[str] = Field(None, max_length=255)
    jaarrente_verzekerd_bedrag: Optional[str] = Field(None, max_length=255)
    werk_omschrijving: Optional[str] = None
    werkzaamheden: Optional[str] = Field(None, max_length=500)
    salaris_uit_nederland: Optional[str] = Field(None, max_length=255)
    loondienst_of_zelfstandig: Optional[str] = Field(None, max_length=255)
    eigen_onderneming_3jaar: Optional[str] = Field(None, max_length=255)
    loon_doorbetaald_bij_ziekte: Optional[str] = Field(None, max_length=500)
    toelichting_uitkering: Optional[str] = None

    # Work conditions
    bouwplaats_of_offshore: Optional[str] = Field(None, max_length=255)
    bouwplaats_hoe_vaak: Optional[str] = Field(None, max_length=255)
    reist_veel_voor_werk: Optional[str] = Field(None, max_length=255)
    frequentie_vervoersmiddel: Optional[str] = None
    gevaarlijke_stoffen: Optional[str] = Field(None, max_length=255)
    toelichting_gevaarlijke_stoffen: Optional[str] = None

    # Health insurance
    interesse_zkv: Optional[str] = Field(None, max_length=255)
    ziektekosten: Optional[str] = Field(None, max_length=255)
    huidige_verzekeraar_ziektekosten: Optional[str] = Field(None, max_length=255)

    # Life insurance
    interesse_levensverzekering: Optional[str] = Field(None, max_length=255)
    levensverzekering: Optional[str] = Field(None, max_length=255)
    rookt: Optional[str] = Field(None, max_length=255)
    gewenste_verzekerde_som: Optional[str] = Field(None, max_length=255)

    # Remarks and marketing
    opmerkingen: Optional[str] = None
    hoe_gevonden: Optional[str] = Field(None, max_length=255)
    opmerkingen_2: Optional[str] = None

    # Raw backup
    raw_form_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('geboortedatum', 'vertrekdatum', 'vertrek_wanneer', 'verwachte_vertrekdatum')
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
