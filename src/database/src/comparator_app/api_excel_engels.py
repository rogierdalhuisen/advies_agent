"""
Import AdviesAanvraagEngels from Excel (English forms).

Mirrors the api_excel.py pattern: read → transform → validate → save.
"""

import pandas as pd
import hashlib
import logging
from typing import Optional, Tuple
from datetime import datetime
from django.db import transaction
from django.utils import timezone as dj_timezone
from pydantic import ValidationError

from .models import AdviesAanvraagEngels
from .api_excel import read_excel_aanvragen, parse_excel_datetime, parse_excel_date, clean_cell_value
from .schemas_engels import AdviesAanvraagEngelsInput

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEL COLUMN → MODEL FIELD MAPPING
# ============================================================================

EXCEL_COLUMN_MAP = {
    # Metadata
    'Datum/tijd': 'ingediend_op',
    'Bron': 'referral_source',
    'Medium': 'referral_medium',
    'Campagne': 'referral_campaign',

    # Personal data
    'I am seeking insurance advice for myself': 'advies_voor_mezelf',
    'Salutation': 'aanhef',
    'Initials and first name': 'voorletters_roepnaam',
    'Surname': 'achternaam',
    'Date of birth': 'geboortedatum',
    'Nationality': 'land_nationaliteit',
    'E-mail': 'email',
    'Phone number': 'telefoonnummer',
    'Permanent place of residence or domicile': 'vaste_woonplaats',

    # Multiple insured persons
    'Multiple insured persons': 'meerdere_verzekerden',

    # Abroad / Situation
    'Destination country': 'bestemming_land',
    'Expected duration of stay': 'verwachte_duur_verblijf',
    'Departure date:': 'vertrekdatum',
    'When did you depart?': 'vertrek_wanneer',
    'Expected departure date:': 'verwachte_vertrekdatum',
    'Reason of residence abroad': 'hoofdreden_verblijf',

    # Work
    'Detailed description of the work you will be doing or or your business': 'werk_omschrijving',
    'What exactly will you be doing abroad? Accurate description of your plans:': 'plannen_omschrijving',

    # Income protection insurance (AOV)
    'Are you interested in an income protection insurance?': 'interesse_aov',
    'Are you employed or self-employed?': 'loondienst_of_zelfstandig',
    'What is your average gross annual income (excluding allowances, etc.) for the past 3 years?': 'bruto_jaarinkomen',
    'What is your (future) gross salary/income in euros - excl. any bonuses, allowances, expense allowances': 'bruto_salaris_inkomen',

    # Health insurance
    'Are you interested in a health insurance?': 'interesse_zkv',
    'For what term are you looking for health insurance?': 'zkv_periode',
    'Description of term and motivation': 'zkv_periode_omschrijving_motivatie',
    'Description of term': 'zkv_periode_omschrijving',
    'Through which insurer are you currently insured?': 'huidige_verzekeraar',
    'Do you have a preference for a specific insurer?': 'voorkeur_verzekeraar',
    'Are there any medical details?': 'medische_bijzonderheden',
    'Explanation of medical details': 'medische_bijzonderheden_toelichting',
    'Do you have specific health insurance needs?': 'specifieke_wensen_zkv',
    'Explanation of needs': 'wensen_toelichting',
    'Should pregnancy and childbirth coverage be included in health insurance?': 'dekking_zwangerschap',
    'Explanation (regarding desired coverage for pregnancy and childbirth)': 'zwangerschap_toelichting',

    # Additional insurances
    'I would also like to receive information on:': 'andere_verzekeringen_interesse',

    # Remarks
    'Remarks': 'opmerkingen',
}

# Excel columns to skip (section headers, non-data columns)
SKIP_COLUMNS = {
    'IP-adres', 'Onderwerp', 'E-mail afzender',
    'Expat and Emigration Advice',
    'Please provide your name and email address. Additionally, indicate your relationship to the person needing insurance advice. Note: When filling out the form, please include the details of the person(s) to be insured.',
    'Please provide the personal data of the principal insured person.',
    'Enter name, date of birth and nationality below for all persons you wish to co-insure.',
    'Abroad',
    'Be sure not to miss our messages after submitting this form.',
}

# Date fields that need date parsing
DATE_FIELDS = {
    'geboortedatum', 'vertrekdatum', 'vertrek_wanneer', 'verwachte_vertrekdatum',
}


# ============================================================================
# DATA EXTRACTION & CONVERSION
# ============================================================================

def generate_external_id(email: str, ingediend_op: str) -> str:
    """Generate a unique external_result_id for Excel rows."""
    raw = f"engels|{email}|{ingediend_op}"
    hash_val = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"excel-engels-{hash_val}"


def transform_excel_row_to_input(
    row: pd.Series,
    row_index: int,
    column_map: dict
) -> Optional[AdviesAanvraagEngelsInput]:
    """
    Transform an Excel row into AdviesAanvraagEngelsInput.

    Args:
        row: Pandas Series (one row)
        row_index: Row number (for logging)
        column_map: Mapping from Excel column → model field

    Returns:
        Validated AdviesAanvraagEngelsInput or None on error
    """
    try:
        # Extract email (REQUIRED)
        email = clean_cell_value(row.get('E-mail'))
        if not email:
            logger.warning(f"Row {row_index}: No email, skip")
            return None

        # Parse ingediend_op
        ingediend_op = parse_excel_datetime(row.get('Datum/tijd'))
        if not ingediend_op:
            ingediend_op = dj_timezone.now()
            logger.warning(f"Row {row_index}: No date/time, using current time")

        # Generate synthetic external_result_id
        external_id = generate_external_id(email, str(ingediend_op))

        # Build input data dictionary
        input_data = {
            'external_result_id': external_id,
            'form_id': 'excel-engels-1',
            'email': email,
            'ingediend_op': ingediend_op,
        }

        # Map all Excel columns to fields
        for excel_col, field_name in column_map.items():
            if excel_col not in row.index:
                continue

            value = row[excel_col]
            cleaned = clean_cell_value(value)
            if cleaned is None:
                continue

            # Special handling for date fields
            if field_name in DATE_FIELDS:
                parsed_date = parse_excel_date(value)
                if parsed_date is not None:
                    input_data[field_name] = parsed_date
                continue

            # Don't overwrite already-set metadata fields
            if field_name in ('ingediend_op', 'email'):
                continue

            # Store string value (skip if already set by an earlier column)
            if field_name not in input_data:
                input_data[field_name] = cleaned

        # Store raw form data for audit
        raw_data = {}
        for col in row.index:
            val = clean_cell_value(row[col])
            if val is not None:
                raw_data[col] = val
        input_data['raw_form_data'] = raw_data

        # Validate with Pydantic
        try:
            validated_input = AdviesAanvraagEngelsInput(**input_data)
            return validated_input
        except ValidationError as e:
            logger.error(f"Row {row_index}: Validation failed: {e}")
            return None

    except Exception as e:
        logger.error(f"Row {row_index}: Transform failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ============================================================================
# SAVE FUNCTION
# ============================================================================

def save_excel_aanvraag_engels(
    validated_input: AdviesAanvraagEngelsInput,
    dry_run: bool = False
) -> Optional[AdviesAanvraagEngels]:
    """
    Save one English AdviesAanvraag with dedup on external_result_id and email + date.
    """
    try:
        result_id = validated_input.external_result_id

        # Check 1: exact same row already imported
        if AdviesAanvraagEngels.objects.filter(external_result_id=result_id).exists():
            logger.debug(f"Result {result_id} already imported (exact ID match), skip")
            return None

        # Check 2: same email + submission date already exists
        if validated_input.ingediend_op and validated_input.email:
            submit_date = validated_input.ingediend_op.date()
            if AdviesAanvraagEngels.objects.filter(
                email=validated_input.email,
                ingediend_op__date=submit_date
            ).exists():
                logger.debug(
                    f"Aanvraag for {validated_input.email} on "
                    f"{submit_date} already exists, skip"
                )
                return None

        if dry_run:
            logger.info(f"[DRY RUN] Would create aanvraag {result_id} for {validated_input.email}")
            from types import SimpleNamespace
            return SimpleNamespace(external_result_id=result_id, email=validated_input.email)

        with transaction.atomic():
            from .api_assuportal import find_or_create_relatie_by_email
            relatie = find_or_create_relatie_by_email(validated_input.email)

            if relatie.relatie_id is None and not relatie.hoofdnaam:
                voornaam = validated_input.voorletters_roepnaam or ''
                achternaam = validated_input.achternaam or ''
                if voornaam or achternaam:
                    relatie.hoofdnaam = f"{voornaam} {achternaam}".strip()
                    relatie.save()

            aanvraag_data = validated_input.model_dump(exclude_none=True)
            aanvraag_data['relatie'] = relatie
            aanvraag = AdviesAanvraagEngels.objects.create(**aanvraag_data)

            naam = f"{aanvraag.voorletters_roepnaam or ''} {aanvraag.achternaam or ''}".strip()
            logger.info(f"Aanvraag (EN) {result_id} saved: {naam} ({validated_input.email})")
            return aanvraag

    except Exception as e:
        logger.error(f"Error saving aanvraag {validated_input.external_result_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ============================================================================
# MAIN SYNC FUNCTION
# ============================================================================

def sync_excel_aanvragen_engels(
    file_path: str,
    max_results: Optional[int] = None,
    dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Import AdviesAanvraagEngels from Excel file.

    Args:
        file_path: Path to the Excel file
        max_results: Maximum number of rows (for testing), None = all
        dry_run: If True, don't actually save to database

    Returns:
        Tuple of (success_count, error_count, skipped_count)
    """
    logger.info(f"=== Start Excel import (Engels) from {file_path} {'(DRY RUN)' if dry_run else ''} ===")

    df = read_excel_aanvragen(file_path)

    if df is None:
        logger.error("Could not read Excel file")
        return 0, 1, 0

    if df.empty:
        logger.warning("Excel file is empty")
        return 0, 0, 0

    # Check for required column
    if 'E-mail' not in df.columns:
        logger.error(f"Column 'E-mail' not found. Available columns: {list(df.columns)}")
        return 0, 1, 0

    # Log unmapped columns for debugging
    mapped_cols = set(EXCEL_COLUMN_MAP.keys())
    actual_cols = set(df.columns)
    unmapped = actual_cols - mapped_cols - SKIP_COLUMNS
    if unmapped:
        logger.info(f"Unmapped columns (will be skipped): {unmapped}")

    # Limit for testing
    if max_results:
        df = df.head(max_results)
        logger.info(f"TEST MODE: Processing only first {max_results} rows")

    success_count = 0
    error_count = 0
    skipped_count = 0

    def process_rows():
        nonlocal success_count, error_count, skipped_count

        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel row number (1-indexed + header)
            logger.debug(f"Processing row {row_num}")

            validated_input = transform_excel_row_to_input(
                row, row_num, EXCEL_COLUMN_MAP
            )

            if not validated_input:
                error_count += 1
                continue

            aanvraag = save_excel_aanvraag_engels(validated_input, dry_run=dry_run)

            if aanvraag:
                success_count += 1
            elif aanvraag is None:
                skipped_count += 1

    if dry_run:
        process_rows()
    else:
        try:
            with transaction.atomic():
                process_rows()
        except Exception as e:
            logger.error(f"CRITICAL: Excel import transaction failed, rolling back: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0, 1, 0

    logger.info(f"=== Excel import (Engels) complete: {success_count} success, {skipped_count} skipped, {error_count} errors ===")
    return success_count, error_count, skipped_count
