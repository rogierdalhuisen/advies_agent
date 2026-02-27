"""
Pydantic schemas for Belgian advice form (AdviesAanvraagBelgie) validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, date


class AdviesAanvraagBelgieInput(BaseModel):
    """
    Validated input data for creating an AdviesAanvraagBelgie.
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

    # Situation and plans
    bestemming_land: Optional[str] = Field(None, max_length=255)
    verwachte_duur_verblijf: Optional[str] = Field(None, max_length=255)
    vertrekdatum: Optional[date] = None
    vertrek_wanneer: Optional[date] = None
    verwachte_vertrekdatum: Optional[date] = None
    hoofdreden_verblijf: Optional[str] = Field(None, max_length=500)

    # Work and income
    werk_omschrijving: Optional[str] = None
    plannen_omschrijving: Optional[str] = None
    salaris_uit_belgie: Optional[str] = Field(None, max_length=255)

    # Disability insurance (AOV)
    interesse_aov: Optional[str] = Field(None, max_length=255)
    loondienst_of_zelfstandig: Optional[str] = Field(None, max_length=255)
    eigen_onderneming_3jaar: Optional[str] = Field(None, max_length=255)
    bruto_jaarinkomen: Optional[str] = Field(None, max_length=255)
    aov_geen_offerte_reden: Optional[str] = None
    loon_doorbetaald_bij_ziekte: Optional[str] = Field(None, max_length=500)
    toelichting_uitkering: Optional[str] = None
    bruto_salaris_inkomen: Optional[str] = Field(None, max_length=255)
    salaris_per_maand_jaar: Optional[str] = Field(None, max_length=255)
    bouwplaats_of_offshore: Optional[str] = Field(None, max_length=255)
    bouwplaats_hoe_vaak: Optional[str] = Field(None, max_length=255)
    gevaarlijke_stoffen: Optional[str] = Field(None, max_length=255)
    toelichting_gevaarlijke_stoffen: Optional[str] = None

    # Health insurance (ZKV)
    interesse_zkv: Optional[str] = Field(None, max_length=255)
    zkv_geen_interesse_reden: Optional[str] = None
    zkv_dekkingsvariant: Optional[str] = Field(None, max_length=255)
    zkv_eigen_risico_voorkeur: Optional[str] = Field(None, max_length=255)
    zkv_eigen_risico_bedrag: Optional[str] = Field(None, max_length=255)
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

    # Sports and activities
    sporten_activiteiten: Optional[str] = None
    sport_semiprofessioneel: Optional[str] = Field(None, max_length=255)
    sport_professioneel_omschrijving: Optional[str] = None

    # Additional insurances
    andere_verzekeringen_interesse: Optional[str] = None
    overlijdensrisico_bedrag: Optional[str] = Field(None, max_length=255)
    overlijdensrisico_bedrag_anders: Optional[str] = Field(None, max_length=255)
    overlijdensrisico_bestemming: Optional[str] = None
    overlijdensrisico_bestemming_anders: Optional[str] = None

    # Remarks
    opmerkingen: Optional[str] = None

    # Marketing and contact
    hoe_gevonden: Optional[str] = Field(None, max_length=255)
    welke_website: Optional[str] = Field(None, max_length=500)
    naam_werkgever: Optional[str] = Field(None, max_length=500)
    hoe_gevonden_overig: Optional[str] = None
    eerder_contact_joho: Optional[str] = Field(None, max_length=255)
    eerder_contact_keuze: Optional[str] = Field(None, max_length=255)
    naam_contactpersoon: Optional[str] = Field(None, max_length=500)
    eerder_contact_anders: Optional[str] = None
    advies_vorm: Optional[str] = Field(None, max_length=255)

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
