"""Main preprocessor for user data.

Combines premium calculation with clean field extraction.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from .pricing.calculator import PremiumCalculator
from .cache import load_from_cache, save_to_cache
from .normalizer import llm_normalize


@dataclass
class PreprocessedUser:
    """Complete preprocessed user data for advice generation.

    All user fields (except premium calculation fields) are directly accessible
    as attributes. Premium data is calculated and stored separately.
    """

    # Identifiers
    aanvraag_id: int
    email: Optional[str] = None

    # Premium calculation results
    premiums: dict = field(default_factory=dict)
    regions: dict = field(default_factory=dict)
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


def preprocess_user(
    email: str | None = None,
    aanvraag_id: int | None = None,
) -> PreprocessedUser:
    """Preprocess user data for advice generation.

    Fetches from Postgres, normalizes fields via LLM, calculates premiums,
    and caches the result.

    Args:
        email: Email to look up (returns most recent aanvraag).
        aanvraag_id: Direct aanvraag ID lookup.

    Returns:
        PreprocessedUser with all data accessible as attributes.

    Raises:
        ValueError: If no user data found or neither email nor aanvraag_id given.

    Example:
        >>> user = preprocess_user(aanvraag_id=92)
        >>> user.bestemming_land
        'Thailand'
        >>> user.wants_zkv
        True
    """
    from src.database.repository import get_by_email, get_by_aanvraag_id

    if email is None and aanvraag_id is None:
        raise ValueError("Provide either email or aanvraag_id")

    # Resolve aanvraag_id from email if needed
    if aanvraag_id is None:
        records = get_by_email(email)
        if not records:
            raise ValueError(f"No user data found for email {email}")
        aanvraag_id = records[0]["aanvraag_id"]

    # Check cache
    cached = load_from_cache(aanvraag_id)
    if cached is not None:
        return cached

    # Fetch from Postgres
    records = get_by_aanvraag_id(aanvraag_id)
    if not records:
        raise ValueError(f"No user data found for aanvraag_id {aanvraag_id}")

    raw = records[0]

    # LLM normalize ambiguous fields (infers bestemming_land, cleans deductible, etc.)
    normalized = llm_normalize(raw)
    raw.update(normalized)

    # Calculate premiums only if we have a destination
    premium_json: dict = {
        "premiums": {},
        "regions": {},
        "family": [],
        "departure_date": None,
        "deductible_requested": None,
    }
    destination = raw.get("bestemming_land")
    if destination and str(destination).strip() and destination != "Onbekend":
        calculator = PremiumCalculator()
        premium_output = calculator.calculate_from_record(raw)
        premium_json = calculator.to_simple_json(premium_output)

    # Parse departure date
    departure_date = None
    raw_departure = premium_json.get("departure_date") or raw.get("vertrekdatum")
    if raw_departure:
        try:
            if isinstance(raw_departure, date):
                departure_date = raw_departure
            else:
                departure_date = date.fromisoformat(str(raw_departure))
        except (ValueError, TypeError):
            pass

    # Build user object with all fields
    user = PreprocessedUser(
        aanvraag_id=aanvraag_id,
        email=raw.get("email"),
        # Premium results
        premiums=premium_json.get("premiums", {}),
        regions=premium_json.get("regions", {}),
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

    # Cache for future use
    save_to_cache(user)

    return user
