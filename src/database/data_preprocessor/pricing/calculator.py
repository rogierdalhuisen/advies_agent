"""Premium calculator for insurance advice."""

from datetime import date
from typing import Optional

import pandas as pd

from .models import (
    CoveragePremium,
    FamilyMember,
    InsurancePremiumResult,
    PremiumCalculationOutput,
    UserPremiumInput,
)
from .loaders import (
    FOLDER_TO_INSURANCE_COLUMN,
    get_all_insurance_folders,
    get_region_for_country,
    load_premium_data,
    load_region_mapping,
    load_user_data,
    parse_deductible_value,
    parse_premium_value,
    parse_user_deductible,
)


# Billing period per provider: "monthly" or "yearly".
# Monthly premiums are multiplied by 12 to normalize all output to yearly amounts.
PROVIDER_BILLING_PERIOD: dict[str, str] = {
    "allianz_globetrotter": "monthly",
    "expatriate_group": "monthly",
    "globality_yougenio": "monthly",
    "goudse_expat_pakket": "yearly",
    "goudse_ngo_zendelingen": "yearly",
    "goudse_working_nomad": "monthly",
    "International Expat Insurance": "monthly",
    "oom_tib": "monthly",
    "oom_wib": "monthly",
    "special_isis": "monthly",
}


class PremiumCalculator:
    """Calculate insurance premiums based on user data. All output premiums are yearly."""

    def __init__(self):
        """Initialize calculator with region mapping."""
        self.region_df = load_region_mapping()
        self._premium_cache: dict[str, list[dict]] = {}

    def _get_premium_data(self, insurance_folder: str) -> Optional[list[dict]]:
        """Get premium data with caching."""
        if insurance_folder not in self._premium_cache:
            data = load_premium_data(insurance_folder)
            if data is not None:
                self._premium_cache[insurance_folder] = data
        return self._premium_cache.get(insurance_folder)

    def _parse_birth_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse birth date string to date object."""
        if not date_str:
            return None
        try:
            return date.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None

    def _extract_family_members(
        self,
        user_record: dict,
        reference_date: Optional[date] = None
    ) -> list[FamilyMember]:
        """
        Extract family members from user record.

        Args:
            user_record: User data dictionary
            reference_date: Date to calculate age as of (departure date).
                           If None, uses today's date.
        """
        members = []

        # Main applicant
        main_bd = self._parse_birth_date(user_record.get('geboortedatum'))
        if main_bd:
            member = FamilyMember(role="main", birth_date=main_bd)
            member.calculate_age(reference_date)
            members.append(member)

        # Partner
        partner_bd = self._parse_birth_date(user_record.get('partner_geboortedatum'))
        if partner_bd:
            member = FamilyMember(role="partner", birth_date=partner_bd)
            member.calculate_age(reference_date)
            members.append(member)

        # Children
        for i in range(1, 5):
            child_bd = self._parse_birth_date(user_record.get(f'kind{i}_geboortedatum'))
            if child_bd:
                member = FamilyMember(role=f"child{i}", birth_date=child_bd)
                member.calculate_age(reference_date)
                members.append(member)

        return members

    def _find_matching_premium(
        self,
        premium_data: list[dict],
        age: int,
        region: Optional[str],
        deductible: Optional[float],
        coverage: str
    ) -> Optional[tuple[float, float]]:
        """
        Find matching premium for age, region, deductible, and coverage.

        Returns:
            Tuple of (premium_value, actual_deductible) or None if no match
        """
        candidates = []

        for record in premium_data:
            # Check coverage match - handle different field names
            record_coverage = record.get('Coverage') or record.get('Plan', '')
            if coverage.lower() not in record_coverage.lower():
                continue

            # Check age match
            min_age = record.get('Min Age')
            max_age = record.get('Max Age')

            # Handle various age formats
            if min_age is not None:
                try:
                    min_age = int(min_age)
                except (ValueError, TypeError):
                    min_age = 0

            if max_age is not None:
                # Handle "+" for unlimited
                if str(max_age) == '+':
                    max_age = 150
                else:
                    try:
                        max_age = int(max_age)
                    except (ValueError, TypeError):
                        max_age = 150

            if min_age is not None and age < min_age:
                continue
            if max_age is not None and age > max_age:
                continue

            # Check region match (if applicable)
            record_region = record.get('Region', '')
            if region:
                # Flexible region matching
                region_lower = region.lower()
                record_region_lower = record_region.lower()

                # Map common region patterns
                region_matches = False
                if region_lower in record_region_lower:
                    region_matches = True
                elif 'regio a' in region_lower and 'europa' in record_region_lower:
                    region_matches = True
                elif 'regio b' in region_lower and 'wereld' in record_region_lower:
                    region_matches = True
                elif region_lower.startswith('europa') and 'a' in record_region_lower:
                    region_matches = True
                elif region_lower.startswith('wereld') and 'b' in record_region_lower:
                    region_matches = True
                elif not record_region:  # Some insurances don't have region
                    region_matches = True

                if not region_matches:
                    continue

            # Parse deductible and premium
            record_deductible = parse_deductible_value(record.get('Deductible'))
            record_premium = parse_premium_value(record.get('Premium'))

            if record_premium is None:
                continue

            candidates.append({
                'deductible': record_deductible or 0,
                'premium': record_premium,
                'coverage': record_coverage,
                'region': record_region,
            })

        if not candidates:
            return None

        # If deductible preference given, find closest lower
        if deductible is not None:
            # Filter to deductibles <= preference
            valid = [c for c in candidates if c['deductible'] <= deductible]
            if valid:
                # Pick the highest deductible that's still <= preference
                best = max(valid, key=lambda x: x['deductible'])
                return (best['premium'], best['deductible'])
            else:
                # No valid deductible found, take lowest available
                best = min(candidates, key=lambda x: x['deductible'])
                return (best['premium'], best['deductible'])
        else:
            # No preference, take lowest deductible
            best = min(candidates, key=lambda x: x['deductible'])
            return (best['premium'], best['deductible'])

    def _get_coverage_levels(self, premium_data: list[dict]) -> list[str]:
        """Extract unique coverage levels from premium data."""
        coverages = set()
        for record in premium_data:
            # Handle different field names
            coverage = record.get('Coverage') or record.get('Plan', '')
            if coverage:
                coverages.add(coverage)
        return sorted(list(coverages))

    def _calculate_insurance_premiums(
        self,
        insurance_folder: str,
        family_members: list[FamilyMember],
        country: Optional[str],
        preferred_deductible: Optional[float]
    ) -> InsurancePremiumResult:
        """Calculate premiums for a single insurance provider."""
        result = InsurancePremiumResult(insurance_name=insurance_folder)

        # Load premium data
        premium_data = self._get_premium_data(insurance_folder)
        if premium_data is None:
            result.has_premiums = False
            result.notes.append("No premium data available")
            return result

        # Get region for this insurance
        region = None
        insurance_column = FOLDER_TO_INSURANCE_COLUMN.get(insurance_folder)
        if insurance_column and country:
            raw_region = get_region_for_country(country, insurance_column, self.region_df)
            region = str(raw_region) if raw_region is not None else None
            result.region_used = region

        # Get all coverage levels
        coverage_levels = self._get_coverage_levels(premium_data)

        for coverage in coverage_levels:
            coverage_result = CoveragePremium(
                coverage_name=coverage,
                deductible=0,
                total_premium=0
            )

            all_eligible = True
            actual_deductible = None

            for member in family_members:
                match = self._find_matching_premium(
                    premium_data,
                    member.age,
                    region,
                    preferred_deductible,
                    coverage
                )

                if match is None:
                    all_eligible = False
                    coverage_result.eligible = False
                    coverage_result.ineligible_reason = (
                        f"{member.role} (age {member.age}) not eligible"
                    )
                    break

                premium, deductible = match
                coverage_result.premium_per_person[member.role] = premium
                coverage_result.total_premium += premium

                if actual_deductible is None:
                    actual_deductible = deductible

            if actual_deductible is not None:
                coverage_result.deductible = actual_deductible

            # Normalize monthly premiums to yearly
            if all_eligible:
                period = PROVIDER_BILLING_PERIOD.get(insurance_folder, "yearly")
                if period == "monthly":
                    coverage_result.total_premium *= 12
                    coverage_result.premium_per_person = {
                        role: amount * 12
                        for role, amount in coverage_result.premium_per_person.items()
                    }

            # Only add if all members are eligible
            if all_eligible:
                result.coverage_premiums.append(coverage_result)

        if not result.coverage_premiums:
            result.notes.append("No eligible coverage levels found for family composition")

        return result

    def calculate_for_user(self, aanvraag_id: int) -> PremiumCalculationOutput:
        """
        Calculate premiums for a specific user request.

        Ages are calculated as of the departure date (vertrekdatum) if provided,
        otherwise as of today's date.

        Args:
            aanvraag_id: The request ID to calculate for

        Returns:
            Complete premium calculation output
        """
        # Load user data
        user_records = load_user_data(aanvraag_id)
        if not user_records:
            raise ValueError(f"No user data found for aanvraag_id {aanvraag_id}")

        user_record = user_records[0]
        return self.calculate_from_record(user_record)

    def calculate_from_record(
        self,
        user_record: dict,
        selected_insurance_folders: Optional[list[str]] = None,
    ) -> PremiumCalculationOutput:
        """
        Calculate premiums from a user record dict directly.

        Ages are calculated as of the departure date (vertrekdatum) if provided,
        otherwise as of today's date.

        Args:
            user_record: User data dictionary
            selected_insurance_folders: Only calculate for these providers.
                If None, calculates for all available providers.

        Returns:
            Complete premium calculation output
        """
        aanvraag_id = user_record.get('aanvraag_id', 0)

        # Get departure date for age calculation (field 175)
        departure_date = self._parse_birth_date(user_record.get('vertrekdatum'))

        # Extract family members with age calculated at departure date
        family_members = self._extract_family_members(user_record, departure_date)
        if not family_members:
            raise ValueError("No valid birth dates found in user data")

        # Get deductible preference
        preferred_deductible = parse_user_deductible(user_record)

        # Get destination country
        country = user_record.get('bestemming_land')

        # Create output
        output = PremiumCalculationOutput(
            aanvraag_id=aanvraag_id,
            family_members=family_members,
            deductible_requested=preferred_deductible,
            departure_date=departure_date,
        )

        # Calculate for selected insurances (or all if none specified)
        insurance_folders = selected_insurance_folders or get_all_insurance_folders()

        for folder in insurance_folders:
            result = self._calculate_insurance_premiums(
                folder,
                family_members,
                country,
                preferred_deductible
            )
            output.results[folder] = result

        return output

    def to_simple_json(self, output: PremiumCalculationOutput) -> dict:
        """
        Convert output to simplified JSON format.

        Returns format:
        {
            "aanvraag_id": 123,
            "family": [...],
            "premiums": {
                "insurance_name": {
                    "coverage_level": price,
                    ...
                },
                ...
            },
            "regions": {
                "insurance_name": "region_name",
                ...
            }
        }
        """
        premiums = {}
        regions = {}

        for insurance_name, result in output.results.items():
            if not result.has_premiums or not result.coverage_premiums:
                continue

            premiums[insurance_name] = {}
            if result.region_used:
                regions[insurance_name] = result.region_used
                
            for coverage in result.coverage_premiums:
                if coverage.eligible:
                    premiums[insurance_name][coverage.coverage_name] = {
                        "total": coverage.total_premium,
                        "deductible": coverage.deductible,
                        "per_person": coverage.premium_per_person,
                    }

        return {
            "aanvraag_id": output.aanvraag_id,
            "calculation_date": output.calculation_date.isoformat(),
            "departure_date": output.departure_date.isoformat() if output.departure_date else None,
            "age_calculated_as_of": (
                output.departure_date.isoformat() if output.departure_date
                else output.calculation_date.isoformat()
            ),
            "deductible_requested": output.deductible_requested,
            "family": [
                {
                    "role": m.role,
                    "age": m.age,
                    "birth_date": m.birth_date.isoformat()
                }
                for m in output.family_members
            ],
            "premiums": premiums,
            "regions": regions,
        }
