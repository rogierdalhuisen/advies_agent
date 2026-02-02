"""LangChain tool wrapper for the premium calculator."""

import json
from datetime import date, timedelta
from typing import Optional

from langchain_core.tools import tool

from src.database.data_preprocessor.pricing.calculator import PremiumCalculator


@tool
def calculate_premiums(
    country: str,
    age: int,
    deductible: float = 250.0,
    insurance_providers: Optional[list[str]] = None,
) -> str:
    """Calculate insurance premiums for a person.

    Args:
        country: Destination country (e.g. "Duitsland", "Thailand")
        age: Age of the person
        deductible: Preferred deductible amount (default 250)
        insurance_providers: List of insurance folder names to calculate for.
            If not provided, calculates for all available providers.

    Returns:
        JSON with premiums per insurance provider and coverage level.
    """
    # Build a synthetic user record with a birth date derived from age
    birth_date = date.today() - timedelta(days=age * 365 + age // 4)
    record = {
        "geboortedatum": birth_date.isoformat(),
        "bestemming_land": country,
        "zkv_eigen_risico_bedrag": str(deductible),
    }

    calculator = PremiumCalculator()
    output = calculator.calculate_from_record(record, insurance_providers)
    result = calculator.to_simple_json(output)
    return json.dumps(result, ensure_ascii=False, indent=2)
