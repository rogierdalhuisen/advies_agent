"""
Import AllianzCareQuote from Excel.

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

from .models import AllianzCareQuote
from .api_excel import read_excel_aanvragen, parse_excel_datetime, parse_excel_date, clean_cell_value
from .schemas_allianz import AllianzCareQuoteInput

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEL COLUMN → MODEL FIELD MAPPING
# ============================================================================

EMAIL_COLUMN = 'Email address'

EXCEL_COLUMN_MAP = {
    # Metadata
    'Datum/tijd': 'ingediend_op',
    'Bron': 'referral_source',
    'Medium': 'referral_medium',
    'Campagne': 'referral_campaign',

    # Personal data
    'First name': 'first_name',
    'Last name': 'last_name',
    'Gender:': 'gender',
    'Email address': 'email',
    'Date of birth': 'geboortedatum',
    'Nationality': 'nationaliteit',

    # Family members
    'Do you also want to insure family members? If yes, please list their date of birth and nationality below.': 'family_members',

    # Location and stay
    'Country of origin': 'country_of_origin',
    'Current country of residence': 'current_country',
    'Destination (future country of residence)': 'destination',
    '\u200bPurpose of stay abroad (living, working, traveling, retirement, other)?': 'purpose_of_stay',
    'Purpose of stay abroad (living, working, traveling, retirement, other)?': 'purpose_of_stay',
    'Expected duration of your stay abroad': 'expected_duration',

    # Coverage
    'Area of Cover': 'area_of_cover',
    'Start date / date of departure': 'start_date',
    'Cover - Inpatient +': 'cover_inpatient',
    'How much deductible would you prefer for inpatient care?': 'deductible_inpatient',
    'How much deductible would you prefer for outpatient care?': 'deductible_outpatient',

    # Remarks
    'Questions or Comments:': 'opmerkingen',
}

# Excel columns to skip (section headers, non-data columns)
SKIP_COLUMNS = {
    'IP-adres', 'Onderwerp', 'E-mail afzender',
}

# Date fields that need date parsing
DATE_FIELDS = {
    'geboortedatum', 'start_date',
}


# ============================================================================
# DATA EXTRACTION & CONVERSION
# ============================================================================

def generate_external_id(email: str, ingediend_op: str) -> str:
    """Generate a unique external_result_id for Excel rows."""
    raw = f"allianz|{email}|{ingediend_op}"
    hash_val = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"excel-allianz-{hash_val}"


def transform_excel_row_to_input(
    row: pd.Series,
    row_index: int,
    column_map: dict
) -> Optional[AllianzCareQuoteInput]:
    """
    Transform an Excel row into AllianzCareQuoteInput.
    """
    try:
        email = clean_cell_value(row.get(EMAIL_COLUMN))
        if not email:
            logger.warning(f"Rij {row_index}: Geen email, skip")
            return None

        ingediend_op = parse_excel_datetime(row.get('Datum/tijd'))
        if not ingediend_op:
            ingediend_op = dj_timezone.now()
            logger.warning(f"Rij {row_index}: Geen datum/tijd, gebruik huidige tijd")

        external_id = generate_external_id(email, str(ingediend_op))

        input_data = {
            'external_result_id': external_id,
            'form_id': 'excel-allianz-1',
            'email': email,
            'ingediend_op': ingediend_op,
        }

        for excel_col, field_name in column_map.items():
            if excel_col not in row.index:
                continue

            value = row[excel_col]
            cleaned = clean_cell_value(value)
            if cleaned is None:
                continue

            if field_name in DATE_FIELDS:
                parsed_date = parse_excel_date(value)
                if parsed_date is not None:
                    input_data[field_name] = parsed_date
                continue

            if field_name in ('ingediend_op', 'email'):
                continue

            if field_name not in input_data:
                input_data[field_name] = cleaned

        # Store raw form data for audit
        raw_data = {}
        for col in row.index:
            val = clean_cell_value(row[col])
            if val is not None:
                raw_data[str(col)] = val
        input_data['raw_form_data'] = raw_data

        try:
            validated_input = AllianzCareQuoteInput(**input_data)
            return validated_input
        except ValidationError as e:
            logger.error(f"Rij {row_index}: Validation failed: {e}")
            return None

    except Exception as e:
        logger.error(f"Rij {row_index}: Transform failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ============================================================================
# SAVE FUNCTION
# ============================================================================

def save_excel_allianz_quote(
    validated_input: AllianzCareQuoteInput,
    dry_run: bool = False
) -> Optional[AllianzCareQuote]:
    """
    Sla één AllianzCareQuote op met dedup op external_result_id en email + datum.
    """
    try:
        result_id = validated_input.external_result_id

        if AllianzCareQuote.objects.filter(external_result_id=result_id).exists():
            logger.debug(f"Result {result_id} al geïmporteerd (exact ID match), skip")
            return None

        if validated_input.ingediend_op and validated_input.email:
            submit_date = validated_input.ingediend_op.date()
            if AllianzCareQuote.objects.filter(
                email=validated_input.email,
                ingediend_op__date=submit_date
            ).exists():
                logger.debug(
                    f"Allianz quote voor {validated_input.email} op "
                    f"{submit_date} bestaat al, skip"
                )
                return None

        if dry_run:
            logger.info(f"[DRY RUN] Would create Allianz quote {result_id} for {validated_input.email}")
            from types import SimpleNamespace
            return SimpleNamespace(external_result_id=result_id, email=validated_input.email)

        with transaction.atomic():
            from .api_assuportal import find_or_create_relatie_by_email
            relatie = find_or_create_relatie_by_email(validated_input.email)

            if relatie.relatie_id is None and not relatie.hoofdnaam:
                first_name = validated_input.first_name or ''
                last_name = validated_input.last_name or ''
                if first_name or last_name:
                    relatie.hoofdnaam = f"{first_name} {last_name}".strip()
                    relatie.save()

            aanvraag_data = validated_input.model_dump(exclude_none=True)
            aanvraag_data['relatie'] = relatie
            quote = AllianzCareQuote.objects.create(**aanvraag_data)

            naam = f"{quote.first_name or ''} {quote.last_name or ''}".strip()
            logger.info(f"Allianz quote {result_id} opgeslagen: {naam} ({validated_input.email})")
            return quote

    except Exception as e:
        logger.error(f"Fout bij opslaan Allianz quote {validated_input.external_result_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ============================================================================
# MAIN SYNC FUNCTION
# ============================================================================

def sync_excel_allianz_quotes(
    file_path: str,
    max_results: Optional[int] = None,
    dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Importeer AllianzCareQuote vanuit Excel bestand.
    """
    logger.info(f"=== Start Excel import (Allianz Care) van {file_path} {'(DRY RUN)' if dry_run else ''} ===")

    df = read_excel_aanvragen(file_path)

    if df is None:
        logger.error("Kon Excel bestand niet lezen")
        return 0, 1, 0

    if df.empty:
        logger.warning("Excel bestand is leeg")
        return 0, 0, 0

    if EMAIL_COLUMN not in df.columns:
        logger.error(f"Kolom '{EMAIL_COLUMN}' niet gevonden. Beschikbare kolommen: {list(df.columns)}")
        return 0, 1, 0

    mapped_cols = set(EXCEL_COLUMN_MAP.keys())
    actual_cols = set(df.columns)
    unmapped = actual_cols - mapped_cols - SKIP_COLUMNS
    if unmapped:
        logger.info(f"Ongemapte kolommen (worden geskipt): {unmapped}")

    if max_results:
        df = df.head(max_results)
        logger.info(f"TEST MODE: Verwerk alleen eerste {max_results} rijen")

    success_count = 0
    error_count = 0
    skipped_count = 0

    def process_rows():
        nonlocal success_count, error_count, skipped_count

        for idx, row in df.iterrows():
            row_num = idx + 2
            logger.debug(f"Verwerk rij {row_num}")

            validated_input = transform_excel_row_to_input(
                row, row_num, EXCEL_COLUMN_MAP
            )

            if not validated_input:
                error_count += 1
                continue

            quote = save_excel_allianz_quote(validated_input, dry_run=dry_run)

            if quote:
                success_count += 1
            elif quote is None:
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

    logger.info(f"=== Excel import (Allianz Care) compleet: {success_count} succesvol, {skipped_count} geskipt, {error_count} fouten ===")
    return success_count, error_count, skipped_count
