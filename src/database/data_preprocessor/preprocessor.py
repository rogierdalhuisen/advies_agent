"""
Main preprocessor for user data.

Combines premium calculation with clean field extraction.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from .pricing.calculator import PremiumCalculator
from .pricing.loaders import load_user_data


@dataclass
class PreprocessedUser:
    """
    Complete preprocessed user data for advice generation.

    All user fields (except premium calculation fields) are directly accessible
    as attributes. Premium data is calculated and stored separately.
    """
    # Identifiers
    aanvraag_id: int
    email: Optional[str] = None

    # Premium calculation results
    premiums: dict = field(default_factory=dict)
    family: list = field(default_factory=list)
    departure_date: Optional[date] = None
    deductible_requested: Optional[float] = None

    # Destination & Travel
    bestemming_land: Optional[str] = None
    vertrekdatum: Optional[str] = None
    hoofdreden_verblijf: Optional[str] = None
    toelichting_hoofdreden: Optional[str] = None
    verwachte_duur_verblijf: Optional[str] = None
    toelichting_duur: Optional[str] = None

    # Work
    functieomschrijving: Optional[str] = None
    type_werkzaamheden: Optional[str] = None
    verwacht_inkomen: Optional[str] = None
    toelichting_verwacht_inkomen: Optional[str] = None

    # Insurance preferences
    interesse_internationale_aov: Optional[str] = None
    interesse_zkv: Optional[str] = None
    zkv_dekkingsvariant: Optional[str] = None
    zkv_eigen_risico_voorkeur: Optional[str] = None
    zkv_eigen_risico_bedrag: Optional[str] = None
    zkv_periode: Optional[str] = None
    zkv_periode_omschrijving_motivatie: Optional[str] = None

    # Current/preferred insurer
    huidige_verzekeraar: Optional[str] = None
    voorkeur_verzekeraar: Optional[str] = None

    # Medical
    medische_bijzonderheden: Optional[str] = None
    medische_bijzonderheden_toelichting: Optional[str] = None

    # Wishes
    specifieke_wensen_zkv: Optional[str] = None
    wensen_toelichting: Optional[str] = None

    # Pregnancy
    dekking_zwangerschap: Optional[str] = None
    zwangerschap_toelichting: Optional[str] = None

    # Sports
    sporten_activiteiten: Optional[str] = None
    sport_semiprofessioneel: Optional[str] = None
    sport_professioneel_omschrijving: Optional[str] = None

    # JoHo contact
    eerder_contact_joho: Optional[str] = None
    eerder_contact_keuze: Optional[str] = None

    # Advice format
    advies_vorm: Optional[str] = None

    # Raw record for any fields not explicitly defined
    _raw: dict = field(default_factory=dict, repr=False)

    # Computed flags
    @property
    def wants_zkv(self) -> bool:
        return (self.interesse_zkv or "").lower() != "nee"

    @property
    def wants_aov(self) -> bool:
        return "ja" in (self.interesse_internationale_aov or "").lower()

    @property
    def has_medical_conditions(self) -> bool:
        return (self.medische_bijzonderheden or "").lower() == "ja"

    @property
    def wants_pregnancy_coverage(self) -> bool:
        return (self.dekking_zwangerschap or "").lower() == "ja"

    @property
    def coverage_preference(self) -> Optional[str]:
        """Returns 'Hoog', 'Medium', 'Laag', or None."""
        pref = (self.zkv_dekkingsvariant or "").lower()
        if "hoog" in pref or "top" in pref:
            return "Hoog"
        elif "gemiddeld" in pref or "medium" in pref:
            return "Medium"
        elif "laag" in pref or "light" in pref:
            return "Laag"
        return None

    def get_cheapest_per_insurance(self) -> dict:
        """Get cheapest coverage option per insurance."""
        result = {}
        for insurance, coverages in self.premiums.items():
            if coverages:
                cheapest = min(coverages.items(), key=lambda x: x[1]["total"])
                result[insurance] = {
                    "coverage": cheapest[0],
                    "total": cheapest[1]["total"],
                    "deductible": cheapest[1]["deductible"],
                }
        return result

    def get_premiums_sorted_by_price(self) -> list:
        """Get all premiums sorted by total price (cheapest first)."""
        all_premiums = []
        for insurance, coverages in self.premiums.items():
            for coverage, details in coverages.items():
                all_premiums.append({
                    "insurance": insurance,
                    "coverage": coverage,
                    "total": details["total"],
                    "deductible": details["deductible"],
                    "per_person": details["per_person"],
                })
        return sorted(all_premiums, key=lambda x: x["total"])


# Fields used for premium calculation (not copied to user object directly)
_PREMIUM_FIELDS = {
    "geboortedatum",
    "land_nationaliteit",
    "partner_geboortedatum",
    "kind1_geboortedatum",
    "kind2_geboortedatum",
    "kind3_geboortedatum",
    "kind4_geboortedatum",
}


def preprocess_user(aanvraag_id: int) -> PreprocessedUser:
    """
    Preprocess user data for advice generation.

    Args:
        aanvraag_id: The request ID to process

    Returns:
        PreprocessedUser with all data accessible as attributes

    Example:
        >>> user = preprocess_user(118)
        >>> user.functieomschrijving
        'Mud-engineer in HDD drilling...'
        >>> user.wants_zkv
        False
        >>> user.get_cheapest_per_insurance()
    """
    records = load_user_data(aanvraag_id)
    if not records:
        raise ValueError(f"No user data found for aanvraag_id {aanvraag_id}")

    raw = records[0]

    # Calculate premiums
    calculator = PremiumCalculator()
    premium_output = calculator.calculate_from_record(raw)
    premium_json = calculator.to_simple_json(premium_output)

    # Parse departure date
    departure_date = None
    if premium_json.get("departure_date"):
        try:
            departure_date = date.fromisoformat(premium_json["departure_date"])
        except (ValueError, TypeError):
            pass

    # Build user object with all fields
    user = PreprocessedUser(
        aanvraag_id=aanvraag_id,
        email=raw.get("email"),
        # Premium results
        premiums=premium_json.get("premiums", {}),
        family=premium_json.get("family", []),
        departure_date=departure_date,
        deductible_requested=premium_json.get("deductible_requested"),
        # Destination & Travel
        bestemming_land=raw.get("bestemming_land"),
        vertrekdatum=raw.get("vertrekdatum"),
        hoofdreden_verblijf=raw.get("hoofdreden_verblijf"),
        toelichting_hoofdreden=raw.get("toelichting_hoofdreden"),
        verwachte_duur_verblijf=raw.get("verwachte_duur_verblijf"),
        toelichting_duur=raw.get("toelichting_duur"),
        # Work
        functieomschrijving=raw.get("functieomschrijving"),
        type_werkzaamheden=raw.get("type_werkzaamheden"),
        verwacht_inkomen=raw.get("verwacht_inkomen"),
        toelichting_verwacht_inkomen=raw.get("toelichting_verwacht_inkomen"),
        # Insurance preferences
        interesse_internationale_aov=raw.get("interesse_internationale_aov"),
        interesse_zkv=raw.get("interesse_zkv"),
        zkv_dekkingsvariant=raw.get("zkv_dekkingsvariant"),
        zkv_eigen_risico_voorkeur=raw.get("zkv_eigen_risico_voorkeur"),
        zkv_eigen_risico_bedrag=raw.get("zkv_eigen_risico_bedrag"),
        zkv_periode=raw.get("zkv_periode"),
        zkv_periode_omschrijving_motivatie=raw.get("zkv_periode_omschrijving_motivatie"),
        # Current/preferred insurer
        huidige_verzekeraar=raw.get("huidige_verzekeraar"),
        voorkeur_verzekeraar=raw.get("voorkeur_verzekeraar"),
        # Medical
        medische_bijzonderheden=raw.get("medische_bijzonderheden"),
        medische_bijzonderheden_toelichting=raw.get("medische_bijzonderheden_toelichting"),
        # Wishes
        specifieke_wensen_zkv=raw.get("specifieke_wensen_zkv"),
        wensen_toelichting=raw.get("wensen_toelichting"),
        # Pregnancy
        dekking_zwangerschap=raw.get("dekking_zwangerschap"),
        zwangerschap_toelichting=raw.get("zwangerschap_toelichting"),
        # Sports
        sporten_activiteiten=raw.get("sporten_activiteiten"),
        sport_semiprofessioneel=raw.get("sport_semiprofessioneel"),
        sport_professioneel_omschrijving=raw.get("sport_professioneel_omschrijving"),
        # JoHo contact
        eerder_contact_joho=raw.get("eerder_contact_joho"),
        eerder_contact_keuze=raw.get("eerder_contact_keuze"),
        # Advice format
        advies_vorm=raw.get("advies_vorm"),
        # Raw for any other fields
        _raw=raw,
    )

    return user


def preprocess_all_users() -> list[PreprocessedUser]:
    """Preprocess all users in the database."""
    records = load_user_data()
    results = []
    for record in records:
        try:
            user = preprocess_user(record["aanvraag_id"])
            results.append(user)
        except Exception as e:
            print(f"Error processing {record.get('aanvraag_id')}: {e}")
    return results
