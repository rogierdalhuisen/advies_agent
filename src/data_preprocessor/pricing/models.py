"""Data models for premium calculation."""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class FamilyMember(BaseModel):
    """Represents a family member for premium calculation."""

    role: str  # "main", "partner", "child1", "child2", "child3", "child4"
    birth_date: date
    age: int = Field(default=0, description="Calculated age")

    def calculate_age(self, reference_date: Optional[date] = None) -> int:
        """Calculate age as of reference date (default: today)."""
        ref = reference_date or date.today()
        age = ref.year - self.birth_date.year
        # Adjust if birthday hasn't occurred yet this year
        if (ref.month, ref.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        self.age = age
        return age


class UserPremiumInput(BaseModel):
    """Input data extracted from user form for premium calculation."""

    aanvraag_id: int
    main_birth_date: date
    partner_birth_date: Optional[date] = None
    child1_birth_date: Optional[date] = None
    child2_birth_date: Optional[date] = None
    child3_birth_date: Optional[date] = None
    child4_birth_date: Optional[date] = None
    destination_country: Optional[str] = None
    preferred_deductible: Optional[float] = None  # Parsed from "€ 500" etc.
    custom_deductible: Optional[float] = None  # From eigen_risico_bedrag


class CoveragePremium(BaseModel):
    """Premium for a specific coverage level."""

    coverage_name: str
    deductible: float
    premium_per_person: dict[str, float] = Field(
        default_factory=dict,
        description="Premium per family member role"
    )
    total_premium: float
    eligible: bool = True
    ineligible_reason: Optional[str] = None


class InsurancePremiumResult(BaseModel):
    """Premium calculation result for a single insurance provider."""

    insurance_name: str
    region_used: Optional[str] = None
    coverage_premiums: list[CoveragePremium] = Field(default_factory=list)
    has_premiums: bool = True
    notes: list[str] = Field(default_factory=list)


class PremiumCalculationOutput(BaseModel):
    """Complete premium calculation output."""

    aanvraag_id: int
    calculation_date: date = Field(default_factory=date.today)
    departure_date: Optional[date] = None  # Age calculated as of this date
    family_members: list[FamilyMember] = Field(default_factory=list)
    deductible_requested: Optional[float] = None
    results: dict[str, InsurancePremiumResult] = Field(default_factory=dict)
