"""
Import AdviesAanvraagWoning from Excel (housing insurance forms).

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

from .models import AdviesAanvraagWoning
from .api_excel import read_excel_aanvragen, parse_excel_datetime, parse_excel_date, clean_cell_value
from .schemas_woning import AdviesAanvraagWoningInput

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

    # Gegevens aanvrager
    'Voornaam': 'voornaam',
    'Achternaam': 'achternaam',
    'Geboortedatum': 'geboortedatum',
    'Geslacht': 'geslacht',
    'E-mailadres': 'email',
    'Telefoonnummer': 'telefoonnummer',
    'Wat is uw nationaliteit?': 'nationaliteit',
    'In welk land (buiten Nederland) woont u of gaat u binnenkort wonen?:': 'woonland_buitenland',
    'Correspondentie adres in Nederland (straat, huisnummer, postcode, plaats)': 'correspondentie_adres_nl',
    'Wanneer bent u vertrokken of gaat u uit Nederland?': 'vertrekdatum',
    'Heeft u zich in Nederland uitgeschreven bij de gemeente (Basisregistratie Personen)?': 'uitgeschreven_brp',

    # Gegevens woning
    'Straatnaam + huisnummer': 'woning_straat_huisnummer',
    'Postcode + Plaats': 'woning_postcode_plaats',
    'Land': 'woning_land',
    'Hoe wordt van de woning gebruik gemaakt?': 'woning_gebruik',
    'Extra informatie m.b.t. het gebruik van de woning': 'woning_gebruik_extra',
    'Soort woning': 'soort_woning',
    'Bouwaard gebouw': 'bouwaard',
    'Dakbedekking': 'dakbedekking',
    'Bijzonderheden aan de woning\u200b (ivm opstalverzekering)': 'bijzonderheden_woning',
    'Extra informatie m.b.t. het soort woning, bouwaard, dakbedekking en bijzonderheden': 'woning_extra_info',

    # Verzekeringen woning
    '\u200b\u200bIn welke verzekering(en) heeft u interesse?': 'interesse_verzekeringen',
    'Wanneer zou u de verzekering(en) willen laten starten?': 'gewenste_startdatum',

    # Verzekeringen buitenland
    'Heeft u interesse in andere (internationale) verzekeringen?': 'interesse_internationale_verzekeringen',

    # Opmerkingen
    'Hier heeft u ruimte voor opmerkingen of toelichting': 'opmerkingen',
}

# Excel columns to skip (section headers, non-data columns)
SKIP_COLUMNS = {
    'IP-adres', 'Onderwerp', 'E-mail afzender',
    'Gegevens aanvrager',
    'Gegevens van de te verzekeren woning',
    'Verzekeringen voor uw woning in Nederland',
    'Verzekeringen voor tijdens uw verblijf in het buitenland',
}

# Date fields that need date parsing
DATE_FIELDS = {
    'geboortedatum', 'vertrekdatum',
}

# Email column name (different from other forms: "E-mailadres" instead of "E-mail")
EMAIL_COLUMN = 'E-mailadres'


# ============================================================================
# DATA EXTRACTION & CONVERSION
# ============================================================================

def generate_external_id(email: str, ingediend_op: str) -> str:
    """Generate a unique external_result_id for Excel rows."""
    raw = f"woning|{email}|{ingediend_op}"
    hash_val = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"excel-woning-{hash_val}"


def transform_excel_row_to_input(
    row: pd.Series,
    row_index: int,
    column_map: dict
) -> Optional[AdviesAanvraagWoningInput]:
    """
    Transform an Excel row into AdviesAanvraagWoningInput.
    """
    try:
        # Note: this form uses "E-mailadres" instead of "E-mail"
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
            'form_id': 'excel-woning-1',
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
            validated_input = AdviesAanvraagWoningInput(**input_data)
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

def save_excel_aanvraag_woning(
    validated_input: AdviesAanvraagWoningInput,
    dry_run: bool = False
) -> Optional[AdviesAanvraagWoning]:
    """
    Sla één woning AdviesAanvraag op met dedup op external_result_id en email + datum.
    """
    try:
        result_id = validated_input.external_result_id

        if AdviesAanvraagWoning.objects.filter(external_result_id=result_id).exists():
            logger.debug(f"Result {result_id} al geïmporteerd (exact ID match), skip")
            return None

        if validated_input.ingediend_op and validated_input.email:
            submit_date = validated_input.ingediend_op.date()
            if AdviesAanvraagWoning.objects.filter(
                email=validated_input.email,
                ingediend_op__date=submit_date
            ).exists():
                logger.debug(
                    f"Aanvraag voor {validated_input.email} op "
                    f"{submit_date} bestaat al, skip"
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
                voornaam = validated_input.voornaam or ''
                achternaam = validated_input.achternaam or ''
                if voornaam or achternaam:
                    relatie.hoofdnaam = f"{voornaam} {achternaam}".strip()
                    relatie.save()

            aanvraag_data = validated_input.model_dump(exclude_none=True)
            aanvraag_data['relatie'] = relatie
            aanvraag = AdviesAanvraagWoning.objects.create(**aanvraag_data)

            naam = f"{aanvraag.voornaam or ''} {aanvraag.achternaam or ''}".strip()
            logger.info(f"Aanvraag (Woning) {result_id} opgeslagen: {naam} ({validated_input.email})")
            return aanvraag

    except Exception as e:
        logger.error(f"Fout bij opslaan aanvraag {validated_input.external_result_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ============================================================================
# MAIN SYNC FUNCTION
# ============================================================================

def sync_excel_aanvragen_woning(
    file_path: str,
    max_results: Optional[int] = None,
    dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Importeer AdviesAanvraagWoning vanuit Excel bestand.
    """
    logger.info(f"=== Start Excel import (Woning) van {file_path} {'(DRY RUN)' if dry_run else ''} ===")

    df = read_excel_aanvragen(file_path)

    if df is None:
        logger.error("Kon Excel bestand niet lezen")
        return 0, 1, 0

    if df.empty:
        logger.warning("Excel bestand is leeg")
        return 0, 0, 0

    # This form uses "E-mailadres" instead of "E-mail"
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

            aanvraag = save_excel_aanvraag_woning(validated_input, dry_run=dry_run)

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

    logger.info(f"=== Excel import (Woning) compleet: {success_count} succesvol, {skipped_count} geskipt, {error_count} fouten ===")
    return success_count, error_count, skipped_count
