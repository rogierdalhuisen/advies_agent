"""LLM-based field normalization for user form data."""

import json
import logging
from functools import lru_cache
from typing import Any

from openai import OpenAI

from src.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Fields that contain PII and must NOT be sent to the LLM
_PII_FIELDS = {
    "email",
    "voorletters_roepnaam",
    "achternaam",
    "telefoonnummer",
    "partner_naam",
    "kind1_naam",
    "kind2_naam",
    "kind3_naam",
    "kind4_naam",
    "naam_contactpersoon",
    "naam_werkgever",
    "eerder_contact_keuze",
    "eerder_contact_anders",
    "ingediend_op",
}

# Fields the LLM must always return
_OUTPUT_FIELDS = {
    "bestemming_land",
    "vertrekdatum",
    "verwachte_duur_verblijf",
    "zkv_eigen_risico_voorkeur",
    "zkv_eigen_risico_bedrag",
}


@lru_cache(maxsize=1)
def _load_country_list() -> list[str]:
    """Load valid country names from regio_mapping.xlsx."""
    from src.preprocessing.pricing.loaders import load_region_mapping

    df = load_region_mapping()
    return sorted(df["LAND"].dropna().unique().tolist())


def _build_system_prompt() -> str:
    """Build system prompt with the actual country list from regio_mapping."""
    countries = _load_country_list()
    country_list_str = ", ".join(f'"{c}"' for c in countries[:50])
    country_list_str += f" ... ({len(countries)} countries total)"

    return f"""\
You are a data normalization assistant for a Dutch insurance advice form. \
You receive ALL non-PII fields from the form as context. Your job is to \
return a JSON object with cleaned/normalized values for these specific fields:

**bestemming_land** (REQUIRED): The destination country. You MUST return a \
country name that EXACTLY matches one from this reference list: \
{json.dumps(countries, ensure_ascii=False)}

IMPORTANT: if the form field `bestemming_land` is empty or missing, you MUST \
infer the destination from other fields such as `toelichting_hoofdreden`, \
`huidig_woonland`, `toelichting_duur`, `functieomschrijving`, or any other \
contextual clue. If multiple countries are mentioned, pick the PRIMARY \
destination. For countries with multiple entries (e.g. "VAE (excl. Dubai)" \
and "VAE (incl. Dubai)"), pick the most likely variant based on context — \
if unsure, pick the inclusive variant. \
Never return null — if you truly cannot determine it, return "Onbekend".

**vertrekdatum**: Return an ISO-8601 date string (YYYY-MM-DD). Parse Dutch \
date formats like "1 maart 2025" or "01-03-2025". If a date object is given, \
return it as YYYY-MM-DD. Return null only if no departure date is found.

**verwachte_duur_verblijf**: Return a structured string like "6 maanden", \
"1 jaar", "2 jaar", "onbepaald". Normalize free-text answers.

**zkv_eigen_risico_voorkeur**: Parse to a clean float as string (e.g. "500.0"). \
Handle values like "€ 500", "500,-", "vijfhonderd". Return null if not present.

**zkv_eigen_risico_bedrag**: Same parsing as above. Return null if not present.

Return valid JSON only. Always include bestemming_land."""


def llm_normalize(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize ambiguous form fields using an LLM.

    Sends all non-PII fields as context so the LLM can infer missing values
    (e.g. destination country from free-text descriptions). The LLM picks
    country names that exactly match regio_mapping.xlsx entries.

    Args:
        raw: Raw user record from the database.

    Returns:
        Dict with normalized field values. Always includes bestemming_land.
    """
    # Send all non-PII fields as context
    context = {}
    for key, value in raw.items():
        if key in _PII_FIELDS:
            continue
        if value is None:
            continue
        context[key] = str(value) if not isinstance(value, (str, int, float, bool)) else value

    if not context:
        return {}

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-5.2-2025-12-11",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
            ],
        )
        result = json.loads(response.choices[0].message.content)
        return {k: v for k, v in result.items() if k in _OUTPUT_FIELDS and v is not None}
    except Exception:
        logger.exception("LLM normalization failed, returning empty dict")
        return {}
