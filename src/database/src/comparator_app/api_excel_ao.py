"""
Import OfferteArbeidsOngeschiktheid from Excel.

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

from .models import OfferteArbeidsOngeschiktheid
from .api_excel import read_excel_aanvragen, parse_excel_datetime, parse_excel_date, clean_cell_value
from .schemas_ao import OfferteArbeidsOngeschiktheidInput

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEL COLUMN → MODEL FIELD MAPPING
# ============================================================================

EMAIL_COLUMN = 'E-mailadres:'

EXCEL_COLUMN_MAP = {
    # Metadata
    'Datum/tijd': 'ingediend_op',
    'Bron': 'referral_source',
    'Medium': 'referral_medium',
    'Campagne': 'referral_campaign',

    # Persoonlijke gegevens
    'Geslacht:': 'geslacht',
    'Achternaam:': 'achternaam',
    'Voorletter(s):': 'voorletters',
    'Geboortedatum:': 'geboortedatum',
    'Telefoonnummer:': 'telefoonnummer',
    'E-mailadres:': 'email',
    'Nationaliteit:': 'nationaliteit',

    # Bestemming en vertrek
    'Bestemming:': 'bestemming_land',
    'Vertrekdatum:': 'vertrekdatum',
    'Wanneer verwacht u te vertrekken?': 'vertrek_wanneer',
    'Wanneer bent u vertrokken?': 'verwachte_vertrekdatum',
    'Verwachte duur van verblijf:': 'verwachte_duur_verblijf',

    # Werk en inkomen
    'Wat is uw bruto inkomen op jaarbasis in euro \u2013 excl. evt. bonussen, toeslagen, onkostenvergoedingen?': 'bruto_jaarinkomen',
    'Jaarrente (verzekerd bedrag):': 'jaarrente_verzekerd_bedrag',
    'Uitgebreide nauwkeurige omschrijving werkzaamheden:': 'werk_omschrijving',
    'Werkzaamheden:': 'werkzaamheden',
    'Blijft u salaris ontvangen uit Nederland?': 'salaris_uit_nederland',
    'Werkt u in loondienst of bent u een zelfstandige?': 'loondienst_of_zelfstandig',
    'Ik heb minimaal 3 jaar aantoonbaar inkomen van mijn eigen onderneming': 'eigen_onderneming_3jaar',
    'Zult u bij ziekte of arbeidsongeschiktheid uw loon doorbetaald krijgen door uw (buitenlandse) werkgever en/of krijgt u vanuit een (buitenlandse) overheidsinstantie een uitkering?': 'loon_doorbetaald_bij_ziekte',
    'Toelichting uitkering': 'toelichting_uitkering',

    # Werkomstandigheden
    'Komt u voor uw werk op bouwplaatsen of productielocaties?': 'bouwplaats_of_offshore',
    'Hoe vaak?': 'bouwplaats_hoe_vaak',
    'Reist u veel voor uw werk?': 'reist_veel_voor_werk',
    'Frequentie en vervoersmiddel': 'frequentie_vervoersmiddel',
    'Komt u in aanraking met machines en/of gevaarlijke stoffen?': 'gevaarlijke_stoffen',
    'Toelichting gevaarlijke stoffen': 'toelichting_gevaarlijke_stoffen',

    # Ziektekostenverzekering
    'Bent u ook geïnteresseerd in een ziektekostenverzekering naast uw arbeidsongeschiktheidsverzekering?': 'interesse_zkv',
    'Ziektekosten:': 'ziektekosten',
    'Bij welke verzekeraar bent u momenteel verzekerd voor ziektekosten?': 'huidige_verzekeraar_ziektekosten',

    # Levensverzekering
    'Bent u ook geïnteresseerd in een levensverzekering (overlijdensrisicoverzekering)?': 'interesse_levensverzekering',
    'Levensverzekering:': 'levensverzekering',
    'Rookt u?': 'rookt',
    'Gewenste verzekerde som': 'gewenste_verzekerde_som',

    # Marketing
    'Hoe heeft u deze site (www.expatverzekering.nl) gevonden?': 'hoe_gevonden',

    # Opmerkingen - there are two "Opmerkingen:" columns
    'Opmerkingen:': 'opmerkingen',
    'Opmerkingen:.1': 'opmerkingen_2',
}

# Excel columns to skip (section headers, non-data columns)
SKIP_COLUMNS = {
    'IP-adres', 'Onderwerp', 'E-mail afzender',
    'Persoonlijke gegevens',
    'Wees er zeker van dat u onze berichten niet mist na het versturen van dit formulier',
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
    raw = f"ao|{email}|{ingediend_op}"
    hash_val = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"excel-ao-{hash_val}"


def transform_excel_row_to_input(
    row: pd.Series,
    row_index: int,
    column_map: dict
) -> Optional[OfferteArbeidsOngeschiktheidInput]:
    """
    Transform an Excel row into OfferteArbeidsOngeschiktheidInput.
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
            'form_id': 'excel-ao-1',
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
            validated_input = OfferteArbeidsOngeschiktheidInput(**input_data)
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

def save_excel_offerte_ao(
    validated_input: OfferteArbeidsOngeschiktheidInput,
    dry_run: bool = False
) -> Optional[OfferteArbeidsOngeschiktheid]:
    """
    Sla één OfferteArbeidsOngeschiktheid op met dedup op external_result_id en email + datum.
    """
    try:
        result_id = validated_input.external_result_id

        if OfferteArbeidsOngeschiktheid.objects.filter(external_result_id=result_id).exists():
            logger.debug(f"Result {result_id} al geïmporteerd (exact ID match), skip")
            return None

        if validated_input.ingediend_op and validated_input.email:
            submit_date = validated_input.ingediend_op.date()
            if OfferteArbeidsOngeschiktheid.objects.filter(
                email=validated_input.email,
                ingediend_op__date=submit_date
            ).exists():
                logger.debug(
                    f"Offerte AO voor {validated_input.email} op "
                    f"{submit_date} bestaat al, skip"
                )
                return None

        if dry_run:
            logger.info(f"[DRY RUN] Would create offerte AO {result_id} for {validated_input.email}")
            from types import SimpleNamespace
            return SimpleNamespace(external_result_id=result_id, email=validated_input.email)

        with transaction.atomic():
            from .api_assuportal import find_or_create_relatie_by_email
            relatie = find_or_create_relatie_by_email(validated_input.email)

            if relatie.relatie_id is None and not relatie.hoofdnaam:
                voorletters = validated_input.voorletters or ''
                achternaam = validated_input.achternaam or ''
                if voorletters or achternaam:
                    relatie.hoofdnaam = f"{voorletters} {achternaam}".strip()
                    relatie.save()

            aanvraag_data = validated_input.model_dump(exclude_none=True)
            aanvraag_data['relatie'] = relatie
            offerte = OfferteArbeidsOngeschiktheid.objects.create(**aanvraag_data)

            naam = f"{offerte.voorletters or ''} {offerte.achternaam or ''}".strip()
            logger.info(f"Offerte AO {result_id} opgeslagen: {naam} ({validated_input.email})")
            return offerte

    except Exception as e:
        logger.error(f"Fout bij opslaan offerte AO {validated_input.external_result_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ============================================================================
# MAIN SYNC FUNCTION
# ============================================================================

def sync_excel_offertes_ao(
    file_path: str,
    max_results: Optional[int] = None,
    dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Importeer OfferteArbeidsOngeschiktheid vanuit Excel bestand.
    """
    logger.info(f"=== Start Excel import (Offerte AO) van {file_path} {'(DRY RUN)' if dry_run else ''} ===")

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

            offerte = save_excel_offerte_ao(validated_input, dry_run=dry_run)

            if offerte:
                success_count += 1
            elif offerte is None:
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

    logger.info(f"=== Excel import (Offerte AO) compleet: {success_count} succesvol, {skipped_count} geskipt, {error_count} fouten ===")
    return success_count, error_count, skipped_count
