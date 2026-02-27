"""
Import AdviesAanvraagBelgie from Excel (Belgian forms).

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

from .models import AdviesAanvraagBelgie
from .api_excel import read_excel_aanvragen, parse_excel_datetime, parse_excel_date, clean_cell_value
from .schemas_belgie import AdviesAanvraagBelgieInput

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

    # Persoonlijke gegevens
    'Ik vraag verzekeringsadvies voor mezelf aan': 'advies_voor_mezelf',
    'Aanhef': 'aanhef',
    'Voorletters en roepnaam': 'voorletters_roepnaam',
    'Achternaam': 'achternaam',
    'Geboortedatum': 'geboortedatum',
    'Nationaliteit': 'land_nationaliteit',
    'E-mail': 'email',
    'Telefoonnummer': 'telefoonnummer',
    'Vaste woon- of verblijfplaats': 'vaste_woonplaats',

    # Meerdere verzekerden
    'Meerdere verzekerden': 'meerdere_verzekerden',

    # Situatie en plannen
    'Land van bestemming': 'bestemming_land',
    'Verwachte duur van verblijf': 'verwachte_duur_verblijf',
    'Vertrekdatum:': 'vertrekdatum',
    'Wanneer bent u vertrokken?': 'vertrek_wanneer',
    'Verwachte vertrekdatum:': 'verwachte_vertrekdatum',
    'Reden van verblijf buiten België': 'hoofdreden_verblijf',

    # Werk en inkomen
    'Nauwkeurige omschrijving van het werk dat u gaat doen of van uw onderneming': 'werk_omschrijving',
    'Wat gaat u precies doen in het buitenland? Nauwkeurige omschrijving van uw plannen': 'plannen_omschrijving',
    'Blijft u salaris ontvangen uit België?': 'salaris_uit_belgie',

    # Arbeidsongeschiktheidsverzekering (AOV)
    'Bent u geïnteresseerd in een offerte voor een arbeidsongeschiktheidsverzekering?': 'interesse_aov',
    'Werkt u in loondienst of bent u zelfstandig?': 'loondienst_of_zelfstandig',
    'Ik heb minimaal 3 jaar aantoonbaar mijn eigen onderneming': 'eigen_onderneming_3jaar',
    'Wat is uw gemiddelde bruto jaarinkomen (excl. toeslagen e.d.) van de afgelopen 3 jaar?': 'bruto_jaarinkomen',
    'Wilt u aangeven wat de reden is waarom u geen offerte wenst te ontvangen?': 'aov_geen_offerte_reden',
    'Zult u bij ziekte of arbeidsongeschiktheid uw loon doorbetaald krijgen door uw (buitenlandse) werkgever en/of krijgt u vanuit een (buitenlandse) overheidsinstantie een uitkering?': 'loon_doorbetaald_bij_ziekte',
    'Toelichting uitkering': 'toelichting_uitkering',
    'Wat is uw (toekomstig) bruto salaris/ inkomen in euro \u2013 excl. evt. bonussen, toeslagen, onkostenvergoedingen': 'bruto_salaris_inkomen',
    'Is het opgegeven salaris/ inkomen per maand of per jaar?': 'salaris_per_maand_jaar',
    'Komt u voor uw werk op bouwplaatsen of productielocaties of werkt u offshore?': 'bouwplaats_of_offshore',
    'Hoe vaak?': 'bouwplaats_hoe_vaak',
    'Komt u in aanraking met machines en/of gevaarlijke stoffen?': 'gevaarlijke_stoffen',
    'Toelichting gevaarlijke stoffen': 'toelichting_gevaarlijke_stoffen',

    # Ziektekostenverzekering (ZKV)
    'Bent u geïnteresseerd in een offerte voor een ziektekostenverzekering?': 'interesse_zkv',
    'Waarom heeft u geen interesse in een offerte ziektekostenverzekering?': 'zkv_geen_interesse_reden',
    'Om goed inzicht te verschaffen in de mogelijkheden hebben we het aanbod van de verzekeraars waar we mee samenwerken ingedeeld in een drietal varianten. Kunt u aangeven voor welke variant u een offerte wenst te ontvangen?': 'zkv_dekkingsvariant',
    'Heeft u voorkeur voor een eigen risico op ziektekosten?': 'zkv_eigen_risico_voorkeur',
    'eigen risico': 'zkv_eigen_risico_bedrag',
    'Voor welke termijn zoekt u een ziektekostenverzekering?': 'zkv_periode',
    'Omschrijving termijn en motivatie': 'zkv_periode_omschrijving_motivatie',
    'Omschrijving termijn': 'zkv_periode_omschrijving',
    'Via welke verzekeraar bent u momenteel verzekerd?': 'huidige_verzekeraar',
    'Heeft u voorkeur voor een specifieke verzekeraar?': 'voorkeur_verzekeraar',
    'Is er sprake van medische bijzonderheden?': 'medische_bijzonderheden',
    'Toelichting medische bijzonderheden': 'medische_bijzonderheden_toelichting',
    'Heeft u specifieke wensen ten aanzien van een ziektekostenverzekering?': 'specifieke_wensen_zkv',
    'Toelichting wensen': 'wensen_toelichting',
    'Moet er dekking voor zwangerschap en bevalling zijn opgenomen in de ziektekostenverzekering?': 'dekking_zwangerschap',
    'Toelichting (mbt de gewenste dekking voor zwangerschap en bevalling)': 'zwangerschap_toelichting',

    # Sporten en activiteiten
    'Welke sport(en) en/of avontuurlijke activiteit(en) beoefent u?': 'sporten_activiteiten',
    'Beoefent u deze sport(en) of activiteit(en) (semi-) professioneel?': 'sport_semiprofessioneel',
    'Welke sporten zijn dit en kunt u het professionele karakter / wedstrijdverband van uw sport omschrijven?': 'sport_professioneel_omschrijving',

    # Aanvullende verzekeringen
    'Ik wil ook informatie ontvangen over:': 'andere_verzekeringen_interesse',
    'Welk bedrag wilt u dat na overlijden wordt uitgekeerd?': 'overlijdensrisico_bedrag',
    'Anders': 'overlijdensrisico_bedrag_anders',
    'Waar is de uitkering voor bestemd': 'overlijdensrisico_bestemming',
    'Anders.1': 'overlijdensrisico_bestemming_anders',

    # Opmerkingen
    'Opmerkingen': 'opmerkingen',

    # Marketing en contact
    'Hoe heeft u ons gevonden?': 'hoe_gevonden',
    'Hoe bent u bij ons terecht gekomen?': 'hoe_gevonden',
    'Welke website?': 'welke_website',
    'Naam van uw werkgever': 'naam_werkgever',
    'Overig': 'hoe_gevonden_overig',
    'Heeft u al contact gehad met JoHo Insurances?': 'eerder_contact_joho',
    'Maak een keuze': 'eerder_contact_keuze',
    'Naam contactpersoon (indien bekend)': 'naam_contactpersoon',
    'Anders.2': 'eerder_contact_anders',
    'In welke vorm wilt u het advies ontvangen? U ontvangt dit per email.': 'advies_vorm',
}

# Excel columns to skip (section headers, non-data columns)
SKIP_COLUMNS = {
    'IP-adres', 'Onderwerp', 'E-mail afzender',
    'Expat- en Emigratieadvies',
    'Wat is uw naam en e-mailadres, en wat is uw relatie tot de persoon die verzekeringsadvies nodig heeft? Let op! Vul in het formulier wel de gegevens in van de te verzekeren persoon / personen.',
    'Persoonlijke gegevens van de hoofdverzekerde',
    'Vul hieronder naam, geboortedatum en nationaliteit in voor alle personen die u wilt meeverzekeren.',
    'Buitenland',
    'Sporten en avontuurlijke activiteiten',
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
    raw = f"belgie|{email}|{ingediend_op}"
    hash_val = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"excel-belgie-{hash_val}"


def transform_excel_row_to_input(
    row: pd.Series,
    row_index: int,
    column_map: dict
) -> Optional[AdviesAanvraagBelgieInput]:
    """
    Transform an Excel row into AdviesAanvraagBelgieInput.
    """
    try:
        email = clean_cell_value(row.get('E-mail'))
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
            'form_id': 'excel-belgie-1',
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
                raw_data[col] = val
        input_data['raw_form_data'] = raw_data

        try:
            validated_input = AdviesAanvraagBelgieInput(**input_data)
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

def save_excel_aanvraag_belgie(
    validated_input: AdviesAanvraagBelgieInput,
    dry_run: bool = False
) -> Optional[AdviesAanvraagBelgie]:
    """
    Sla één Belgische AdviesAanvraag op met dedup op external_result_id en email + datum.
    """
    try:
        result_id = validated_input.external_result_id

        if AdviesAanvraagBelgie.objects.filter(external_result_id=result_id).exists():
            logger.debug(f"Result {result_id} al geïmporteerd (exact ID match), skip")
            return None

        if validated_input.ingediend_op and validated_input.email:
            submit_date = validated_input.ingediend_op.date()
            if AdviesAanvraagBelgie.objects.filter(
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
                voornaam = validated_input.voorletters_roepnaam or ''
                achternaam = validated_input.achternaam or ''
                if voornaam or achternaam:
                    relatie.hoofdnaam = f"{voornaam} {achternaam}".strip()
                    relatie.save()

            aanvraag_data = validated_input.model_dump(exclude_none=True)
            aanvraag_data['relatie'] = relatie
            aanvraag = AdviesAanvraagBelgie.objects.create(**aanvraag_data)

            naam = f"{aanvraag.voorletters_roepnaam or ''} {aanvraag.achternaam or ''}".strip()
            logger.info(f"Aanvraag (BE) {result_id} opgeslagen: {naam} ({validated_input.email})")
            return aanvraag

    except Exception as e:
        logger.error(f"Fout bij opslaan aanvraag {validated_input.external_result_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ============================================================================
# MAIN SYNC FUNCTION
# ============================================================================

def sync_excel_aanvragen_belgie(
    file_path: str,
    max_results: Optional[int] = None,
    dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Importeer AdviesAanvraagBelgie vanuit Excel bestand.
    """
    logger.info(f"=== Start Excel import (België) van {file_path} {'(DRY RUN)' if dry_run else ''} ===")

    df = read_excel_aanvragen(file_path)

    if df is None:
        logger.error("Kon Excel bestand niet lezen")
        return 0, 1, 0

    if df.empty:
        logger.warning("Excel bestand is leeg")
        return 0, 0, 0

    if 'E-mail' not in df.columns:
        logger.error(f"Kolom 'E-mail' niet gevonden. Beschikbare kolommen: {list(df.columns)}")
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

            aanvraag = save_excel_aanvraag_belgie(validated_input, dry_run=dry_run)

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

    logger.info(f"=== Excel import (België) compleet: {success_count} succesvol, {skipped_count} geskipt, {error_count} fouten ===")
    return success_count, error_count, skipped_count
