"""
Pydantic schemas for AllianzCareQuote validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, date


class AllianzCareQuoteInput(BaseModel):
    """
    Validated input data for creating an AllianzCareQuote.
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
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    gender: Optional[str] = Field(None, max_length=50)
    geboortedatum: Optional[date] = None
    nationaliteit: Optional[str] = Field(None, max_length=255)

    # Family members
    family_members: Optional[str] = None

    # Location and stay
    country_of_origin: Optional[str] = Field(None, max_length=255)
    current_country: Optional[str] = Field(None, max_length=255)
    destination: Optional[str] = Field(None, max_length=255)
    purpose_of_stay: Optional[str] = Field(None, max_length=500)
    expected_duration: Optional[str] = Field(None, max_length=255)

    # Coverage
    area_of_cover: Optional[str] = Field(None, max_length=255)
    start_date: Optional[date] = None
    cover_inpatient: Optional[str] = Field(None, max_length=255)
    deductible_inpatient: Optional[str] = Field(None, max_length=255)
    deductible_outpatient: Optional[str] = Field(None, max_length=255)

    # Remarks
    opmerkingen: Optional[str] = None

    # Raw backup
    raw_form_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('geboortedatum', 'start_date')
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
