"""Pydantic models for AdviesAanvragen data.

These models are intentionally lenient to handle messy form data.
All fields are optional and use permissive type coercion.
"""

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


def safe_str(value: Any) -> Optional[str]:
    """Safely convert value to string, returning None for empty/invalid values."""
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return str(value)


def safe_date(value: Any) -> Optional[date]:
    """Safely parse date from various formats."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        # Try common formats
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    return None


def safe_datetime(value: Any) -> Optional[datetime]:
    """Safely parse datetime from various formats."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        # Try common formats
        for fmt in [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d",
        ]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def safe_bool(value: Any) -> Optional[bool]:
    """Safely convert value to boolean."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.lower().strip()
        if lower in ("true", "yes", "ja", "1", "t", "y"):
            return True
        if lower in ("false", "no", "nee", "0", "f", "n"):
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return None


class AdviesAanvraag(BaseModel):
    """Model for insurance advice requests (AdviesAanvragen).

    All fields are optional and use lenient parsing to handle messy form data.
    """

    model_config = {
        "strict": False,
        "from_attributes": True,
        "populate_by_name": True,
        "extra": "allow",  # Allow extra fields from DB
    }

    # Primary key and relations
    aanvraag_id: Optional[int] = None
    relatie_id: Optional[int] = None

    # Metadata
    external_result_id: Optional[str] = None
    form_id: Optional[str] = None
    ingediend_op: Optional[datetime] = None
    referral_source: Optional[str] = None
    referral_medium: Optional[str] = None
    referral_campaign: Optional[str] = None
    aangemaakt_op: Optional[datetime] = None

    # Personal info (Hoofdverzekerde)
    advies_voor_mezelf: Optional[str] = None
    aanhef: Optional[str] = None
    voorletters_roepnaam: Optional[str] = None
    achternaam: Optional[str] = None
    geboortedatum: Optional[date] = None
    land_nationaliteit: Optional[str] = None
    email: Optional[str] = None
    telefoonnummer: Optional[str] = None
    vaste_woonplaats: Optional[str] = None
    geen_vaste_woonplaats: Optional[bool] = None

    # Multiple insured persons
    meerdere_verzekerden: Optional[str] = None
    partner_naam: Optional[str] = None
    partner_geboortedatum: Optional[date] = None
    partner_nationaliteit: Optional[str] = None

    kind1_naam: Optional[str] = None
    kind1_geboortedatum: Optional[date] = None
    kind1_nationaliteit: Optional[str] = None

    kind2_naam: Optional[str] = None
    kind2_geboortedatum: Optional[date] = None
    kind2_nationaliteit: Optional[str] = None

    kind3_naam: Optional[str] = None
    kind3_geboortedatum: Optional[date] = None
    kind3_nationaliteit: Optional[str] = None

    kind4_naam: Optional[str] = None
    kind4_geboortedatum: Optional[date] = None
    kind4_nationaliteit: Optional[str] = None

    anders_personen: Optional[str] = None

    # Situation and plans
    situatie_type: Optional[str] = None
    bestemming_land: Optional[str] = None
    vertrekdatum: Optional[date] = None
    uitschrijven_brp: Optional[str] = None
    huidig_woonland: Optional[str] = None
    advies_voor: Optional[str] = None
    hoofdreden_verblijf: Optional[str] = None
    toelichting_hoofdreden: Optional[str] = None
    verwachte_duur_verblijf: Optional[str] = None
    toelichting_duur: Optional[str] = None

    # Work and income
    werk_omschrijving: Optional[str] = None
    plannen_omschrijving: Optional[str] = None
    salaris_uit_nederland: Optional[str] = None

    # Disability insurance (AOV)
    interesse_aov: Optional[str] = None
    loondienst_of_zelfstandig: Optional[str] = None
    eigen_onderneming_3jaar: Optional[str] = None
    bruto_jaarinkomen: Optional[str] = None
    aov_geen_offerte_reden: Optional[str] = None
    loon_doorbetaald_bij_ziekte: Optional[str] = None
    toelichting_uitkering: Optional[str] = None
    bruto_salaris_inkomen: Optional[str] = None
    salaris_per_maand_jaar: Optional[str] = None
    bouwplaats_of_offshore: Optional[str] = None
    bouwplaats_hoe_vaak: Optional[str] = None
    gevaarlijke_stoffen: Optional[str] = None
    toelichting_gevaarlijke_stoffen: Optional[str] = None
    interesse_internationale_aov: Optional[str] = None
    geen_interesse_aov_reden: Optional[str] = None
    functieomschrijving: Optional[str] = None
    type_werkzaamheden: Optional[str] = None
    verwacht_inkomen: Optional[str] = None
    inkomen_toelichting: Optional[str] = None

    # Health insurance (ZKV)
    interesse_zkv: Optional[str] = None
    zkv_geen_interesse_reden: Optional[str] = None
    zkv_dekkingsvariant: Optional[str] = None
    zkv_eigen_risico_voorkeur: Optional[str] = None
    zkv_eigen_risico_bedrag: Optional[str] = None
    zkv_periode: Optional[str] = None
    zkv_periode_omschrijving_motivatie: Optional[str] = None
    zkv_periode_omschrijving: Optional[str] = None
    huidige_verzekeraar: Optional[str] = None
    voorkeur_verzekeraar: Optional[str] = None
    medische_bijzonderheden: Optional[str] = None
    medische_bijzonderheden_toelichting: Optional[str] = None
    specifieke_wensen_zkv: Optional[str] = None
    wensen_toelichting: Optional[str] = None
    dekking_zwangerschap: Optional[str] = None
    zwangerschap_toelichting: Optional[str] = None

    # Additional insurances
    andere_verzekeringen_interesse: Optional[str] = None
    overlijdensrisico_bedrag: Optional[str] = None
    overlijdensrisico_bedrag_anders: Optional[str] = None
    overlijdensrisico_bestemming: Optional[str] = None
    overlijdensrisico_bestemming_anders: Optional[str] = None

    # Sports and activities
    sporten_activiteiten: Optional[str] = None
    sport_semiprofessioneel: Optional[str] = None
    sport_professioneel_omschrijving: Optional[str] = None

    # House in Netherlands
    huis_in_nederland: Optional[str] = None
    huis_type: Optional[str] = None
    woning_verhuurd: Optional[str] = None
    woning_eigen_gebruik: Optional[str] = None
    woning_verblijf_frequentie: Optional[str] = None
    woning_opmerkingen: Optional[str] = None

    # Marketing and contact
    hoe_gevonden: Optional[str] = None
    welke_website: Optional[str] = None
    naam_werkgever: Optional[str] = None
    hoe_gevonden_overig: Optional[str] = None
    eerder_contact_joho: Optional[str] = None
    eerder_contact_keuze: Optional[str] = None
    naam_contactpersoon: Optional[str] = None
    eerder_contact_anders: Optional[str] = None
    advies_vorm: Optional[str] = None

    # Raw data backup
    raw_form_data: Optional[dict] = None

    # Validators for date fields
    @field_validator(
        "geboortedatum",
        "partner_geboortedatum",
        "kind1_geboortedatum",
        "kind2_geboortedatum",
        "kind3_geboortedatum",
        "kind4_geboortedatum",
        "vertrekdatum",
        mode="before",
    )
    @classmethod
    def parse_date(cls, v):
        return safe_date(v)

    @field_validator("ingediend_op", "aangemaakt_op", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        return safe_datetime(v)

    @field_validator("geen_vaste_woonplaats", mode="before")
    @classmethod
    def parse_bool(cls, v):
        return safe_bool(v)

    @model_validator(mode="before")
    @classmethod
    def handle_messy_data(cls, data):
        """Pre-process messy data before validation."""
        if isinstance(data, dict):
            # Strip whitespace from string values
            cleaned = {}
            for key, value in data.items():
                if isinstance(value, str):
                    stripped = value.strip()
                    cleaned[key] = stripped if stripped else None
                else:
                    cleaned[key] = value
            return cleaned
        return data

    # Convenience properties
    @property
    def full_name(self) -> str:
        """Get full name of the main insured person."""
        parts = [self.voorletters_roepnaam, self.achternaam]
        return " ".join(p for p in parts if p) or "Onbekend"

    @property
    def destination(self) -> Optional[str]:
        """Get destination country (bestemming or current residence)."""
        return self.bestemming_land or self.huidig_woonland

    @property
    def family_members(self) -> list[dict]:
        """Get list of family members to be insured."""
        members = []

        if self.partner_naam:
            members.append({
                "type": "partner",
                "name": self.partner_naam,
                "birth_date": self.partner_geboortedatum,
                "nationality": self.partner_nationaliteit,
            })

        for i in range(1, 5):
            name = getattr(self, f"kind{i}_naam", None)
            if name:
                members.append({
                    "type": "kind",
                    "name": name,
                    "birth_date": getattr(self, f"kind{i}_geboortedatum", None),
                    "nationality": getattr(self, f"kind{i}_nationaliteit", None),
                })

        return members

    @property
    def wants_health_insurance(self) -> bool:
        """Check if applicant is interested in health insurance."""
        if self.interesse_zkv:
            return self.interesse_zkv.lower() in ("ja", "yes", "true", "1")
        return False

    @property
    def wants_disability_insurance(self) -> bool:
        """Check if applicant is interested in disability insurance."""
        if self.interesse_aov:
            return self.interesse_aov.lower() in ("ja", "yes", "true", "1")
        return False

    def to_context_dict(self) -> dict:
        """Convert to a dictionary suitable for RAG context.

        Returns a cleaned dict with only non-None values and
        grouped by category for easier consumption.
        """
        return {
            "personal_info": {
                "name": self.full_name,
                "birth_date": str(self.geboortedatum) if self.geboortedatum else None,
                "nationality": self.land_nationaliteit,
                "email": self.email,
                "phone": self.telefoonnummer,
                "residence": self.vaste_woonplaats,
            },
            "family": {
                "has_partner": self.partner_naam is not None,
                "num_children": len([m for m in self.family_members if m["type"] == "kind"]),
                "members": self.family_members,
            },
            "travel_plans": {
                "destination": self.destination,
                "departure_date": str(self.vertrekdatum) if self.vertrekdatum else None,
                "expected_duration": self.verwachte_duur_verblijf,
                "main_reason": self.hoofdreden_verblijf,
                "unregister_brp": self.uitschrijven_brp,
            },
            "work": {
                "description": self.werk_omschrijving,
                "plans": self.plannen_omschrijving,
                "salary_from_nl": self.salaris_uit_nederland,
                "employment_type": self.loondienst_of_zelfstandig,
                "job_title": self.functieomschrijving,
            },
            "insurance_preferences": {
                "health_insurance": {
                    "interested": self.wants_health_insurance,
                    "coverage_level": self.zkv_dekkingsvariant,
                    "deductible_preference": self.zkv_eigen_risico_voorkeur,
                    "current_insurer": self.huidige_verzekeraar,
                    "preferred_insurer": self.voorkeur_verzekeraar,
                    "pregnancy_coverage": self.dekking_zwangerschap,
                    "special_wishes": self.wensen_toelichting,
                },
                "disability_insurance": {
                    "interested": self.wants_disability_insurance,
                    "annual_income": self.bruto_jaarinkomen,
                },
                "other_insurances": self.andere_verzekeringen_interesse,
            },
            "medical": {
                "has_conditions": self.medische_bijzonderheden,
                "details": self.medische_bijzonderheden_toelichting,
            },
            "sports_activities": self.sporten_activiteiten,
        }
