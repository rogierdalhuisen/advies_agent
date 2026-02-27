"""
Import AdviesAanvragen from Excel (old forms).

Mirrors the api_egrip.py pattern: fetch → transform → validate → save.
Instead of an API call, data is read from an Excel file via pandas.
"""

import pandas as pd
import hashlib
import logging
from typing import Optional, Tuple
from datetime import datetime, date
from django.db import transaction
from django.utils import timezone as dj_timezone
from pydantic import ValidationError

from .models import AdviesAanvragen
from .api_egrip import parse_date_value, parse_boolean_value, DATE_FIELDS, BOOLEAN_FIELDS
from .schemas_egrip import AdviesAanvraagInput

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEL COLUMN → MODEL FIELD MAPPING
# ============================================================================

# Maps Excel column name → AdviesAanvragen field name.
# Pandas auto-suffixes duplicate column names (.1, .2, etc.).
EXCEL_COLUMN_MAP = {
    # Metadata
    'Datum/tijd': 'ingediend_op',
    'Bron': 'referral_source',
    'Medium': 'referral_medium',
    'Campagne': 'referral_campaign',

    # Persoonlijke gegevens hoofdverzekerde
    'Ik vraag verzekeringsadvies voor mezelf aan': 'advies_voor_mezelf',
    'Aanhef': 'aanhef',
    'Voorletters en roepnaam': 'voorletters_roepnaam',
    'Achternaam': 'achternaam',
    'Geboortedatum': 'geboortedatum',
    'Land van nationaliteit': 'land_nationaliteit',
    'E-mail': 'email',
    'Telefoonnummer': 'telefoonnummer',
    'Vaste woon- of verblijfplaats': 'vaste_woonplaats',

    # Meerdere verzekerden
    'Meerdere verzekerden': 'meerdere_verzekerden',
    'Naam partner': 'partner_naam',
    'Geboortedatum partner': 'partner_geboortedatum',
    'Land van nationaliteit partner': 'partner_nationaliteit',

    # Kind 1 (first occurrence — no suffix)
    'Naam kind': 'kind1_naam',
    'Geboortedatum kind': 'kind1_geboortedatum',
    'Land van nationaliteit kind': 'kind1_nationaliteit',

    # Kind 2 (pandas adds .1 suffix)
    'Naam kind.1': 'kind2_naam',
    'Geboortedatum kind.1': 'kind2_geboortedatum',
    'Land van nationaliteit kind.1': 'kind2_nationaliteit',

    # Kind 3
    'Naam kind.2': 'kind3_naam',
    'Geboortedatum kind.2': 'kind3_geboortedatum',
    'Land van nationaliteit kind.2': 'kind3_nationaliteit',

    # Kind 4
    'Naam kind.3': 'kind4_naam',
    'Geboortedatum kind.3': 'kind4_geboortedatum',
    'Land van nationaliteit kind.3': 'kind4_nationaliteit',

    'Anders': 'anders_personen',

    # Situatie en plannen
    'Uw situatie en plannen': 'situatie_type',
    'Land van bestemming (meerdere keuzes mogelijk)': 'bestemming_land',
    'Vertrekdatum:': 'vertrekdatum',
    'Gaat u zich uitschrijven uit de gemeente (Basisregistratie Personen - BRP) of heeft u zich uitgeschreven?': 'uitschrijven_brp',
    'Huidig woonland': 'huidig_woonland',
    'Ik zoek advies voor': 'advies_voor',
    'Hoofdreden van verblijf in het buitenland': 'hoofdreden_verblijf',
    'Toelichting': 'toelichting_hoofdreden',
    'Verwachte duur van verblijf in het buitenland:': 'verwachte_duur_verblijf',
    'Toelichting.1': 'toelichting_duur',

    # Werk en inkomen
    'Nauwkeurige omschrijving van het werk dat u gaat doen of van uw onderneming': 'werk_omschrijving',
    'Wat gaat u precies doen in het buitenland? Nauwkeurige omschrijving van uw plannen': 'plannen_omschrijving',
    'Blijft u salaris ontvangen uit Nederland?': 'salaris_uit_nederland',

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
    'Bent u geïnteresseerd in informatie over internationale arbeidsongeschiktheidsverzekeringen?': 'interesse_internationale_aov',
    'Wilt u aangeven wat de reden is waarom u geen informatie wenst te ontvangen?': 'geen_interesse_aov_reden',
    'Functieomschrijving': 'functieomschrijving',
    'Type werkzaamheden': 'type_werkzaamheden',
    'Uw verwachte inkomen uit werkzaamheden (\u20ac/$ per jaar/maand)': 'verwacht_inkomen',
    'Toelichting.2': 'inkomen_toelichting',

    # Ziektekostenverzekering (ZKV)
    'Bent u geïnteresseerd in een offerte voor een ziektekostenverzekering?': 'interesse_zkv',
    'Kunt u aangeven waarom u geen interesse heeft in informatie over ziektekostenverzekeringen?': 'zkv_geen_interesse_reden',
    'Om goed inzicht te verschaffen in de mogelijkheden hebben we het aanbod van de verzekeraars waar we mee samenwerken ingedeeld in een drietal varianten. Kunt u aangeven voor welke variant u een offerte wenst te ontvangen?': 'zkv_dekkingsvariant',
    'Heeft u voorkeur voor een eigen risico op ziektekosten?': 'zkv_eigen_risico_voorkeur',
    'eigen risico': 'zkv_eigen_risico_bedrag',
    'Voor welke periode zoekt u een ziektekostenverzekering?': 'zkv_periode',
    'Omschrijving termijn en motivatie ': 'zkv_periode_omschrijving_motivatie',
    'Omschrijving periode': 'zkv_periode_omschrijving',
    'Via welke verzekeraar bent u momenteel verzekerd?': 'huidige_verzekeraar',
    'Heeft u voorkeur voor een specifieke verzekeraar?': 'voorkeur_verzekeraar',
    'Is er sprake van medische bijzonderheden?': 'medische_bijzonderheden',
    'Toelichting medische bijzonderheden': 'medische_bijzonderheden_toelichting',
    'Heeft u specifieke wensen ten aanzien van een ziektekostenverzekering?': 'specifieke_wensen_zkv',
    'Toelichting wensen': 'wensen_toelichting',
    'Moet er dekking voor zwangerschap en bevalling zijn opgenomen in de ziektekostenverzekering?': 'dekking_zwangerschap',
    'Toelichting (mbt de gewenste dekking voor zwangerschap en bevalling)': 'zwangerschap_toelichting',

    # Aanvullende verzekeringen
    'Ik wil ook informatie ontvangen over:': 'andere_verzekeringen_interesse',
    'Welk bedrag wilt u dat na overlijden wordt uitgekeerd? ': 'overlijdensrisico_bedrag',
    'Anders.1': 'overlijdensrisico_bedrag_anders',
    'Waar is de uitkering voor bestemd ': 'overlijdensrisico_bestemming',
    'Anders.2': 'overlijdensrisico_bestemming_anders',

    # Sporten en activiteiten
    'Welke sport(en) en/of avontuurlijke activiteit(en) beoefent u?': 'sporten_activiteiten',
    'Beoefent u deze sport(en) of activiteit(en) (semi-) professioneel?': 'sport_semiprofessioneel',
    'Welke sporten zijn dit en kunt u het professionele karakter / wedstrijdverband van uw sport omschrijven?': 'sport_professioneel_omschrijving',

    # Huis in Nederland
    'Houdt u een eigen woning aan in Nederland?': 'huis_in_nederland',
    'Betreft het een huis of een appartement?': 'huis_type',
    'Wordt de woning verhuurd? ': 'woning_verhuurd',
    'Maakt u zelf gebruik van de woning? ': 'woning_eigen_gebruik',
    'Jaarlijkse frequentie van verblijf en duur van uw verblijf in de woning?': 'woning_verblijf_frequentie',
    'Opmerkingen': 'woning_opmerkingen',

    # Marketing en contact
    'Hoe heeft u ons gevonden?': 'hoe_gevonden',
    'Hoe bent u bij ons terecht gekomen?': 'hoe_gevonden',
    'Welke website?': 'welke_website',
    'Naam van uw werkgever': 'naam_werkgever',
    'Overig': 'hoe_gevonden_overig',
    'Heeft u al contact gehad met en/of bent u al eerder verzekerd geweest via JoHo Insurances?': 'eerder_contact_joho',
    'Maak een keuze': 'eerder_contact_keuze',
    'Naam contactpersoon (indien bekend)': 'naam_contactpersoon',
    'Anders.3': 'eerder_contact_anders',
    'In welke vorm wilt u het advies ontvangen? U ontvangt dit per email.': 'advies_vorm',
}

# Excel columns to skip (section headers, non-data columns)
SKIP_COLUMNS = {
    'IP-adres', 'Onderwerp', 'E-mail afzender',
    'Expat- en Emigratieadvies',
    'Wat is uw naam en e-mailadres, en wat is uw relatie tot de persoon die verzekeringsadvies nodig heeft? Let op! Vul in het formulier wel de gegevens in van de te verzekeren persoon / personen.',
    'Persoonlijke gegevens van de hoofdverzekerde',
    'Buitenland', 'Verzekeringen',
    'Sporten en avontuurlijke activiteiten',
    'Huis in Nederland',
}

# Date fields that need parsing from Excel
EXCEL_DATE_FIELDS = DATE_FIELDS  # Same as E-grip


# ============================================================================
# EXCEL READ FUNCTION
# ============================================================================

def read_excel_aanvragen(file_path: str) -> Optional[pd.DataFrame]:
    """
    Lees Excel bestand met aanvragen.

    Probeert eerst openpyxl (standaard), dan calamine als fallback
    voor bestanden met non-standard XML namespaces.

    Args:
        file_path: Pad naar het Excel bestand

    Returns:
        DataFrame of None bij fout
    """
    engines = ['openpyxl', 'calamine', 'xlrd']

    for engine in engines:
        try:
            df = pd.read_excel(file_path, engine=engine)
            logger.info(f"Excel gelezen met engine '{engine}': {len(df)} rijen, {len(df.columns)} kolommen")
            logger.info(f"Kolommen: {list(df.columns)}")
            return df
        except ImportError:
            logger.debug(f"Engine '{engine}' niet beschikbaar, probeer volgende")
            continue
        except FileNotFoundError:
            logger.error(f"Excel bestand niet gevonden: {file_path}")
            return None
        except Exception as e:
            logger.debug(f"Engine '{engine}' kon bestand niet lezen: {e}")
            continue

    # Fallback: try reading as HTML table (some web exports save HTML as .xls)
    try:
        dfs = pd.read_html(file_path, header=0)
        if dfs:
            df = dfs[0]
            logger.info(f"Excel gelezen als HTML tabel: {len(df)} rijen, {len(df.columns)} kolommen")
            logger.info(f"Kolommen: {list(df.columns)}")
            return df
    except Exception as e:
        logger.debug(f"HTML fallback kon bestand niet lezen: {e}")

    logger.error(
        f"Kon Excel niet lezen met beschikbare engines. "
        f"Installeer python-calamine (pip install python-calamine) of xlrd (pip install xlrd)."
    )
    return None


# ============================================================================
# DATA EXTRACTION & CONVERSION
# ============================================================================

def generate_external_id(email: str, ingediend_op: str) -> str:
    """
    Genereer een uniek external_result_id voor Excel rijen.

    Args:
        email: Email adres
        ingediend_op: Datum/tijd string

    Returns:
        Uniek ID in formaat 'excel-{hash}'
    """
    raw = f"{email}|{ingediend_op}"
    hash_val = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"excel-{hash_val}"


def parse_excel_datetime(value) -> Optional[datetime]:
    """
    Parse datum/tijd uit Excel. Pandas kan dit als datetime, string of NaT teruggeven.

    Args:
        value: Waarde uit Excel kolom

    Returns:
        datetime object of None
    """
    if pd.isna(value):
        return None

    # Already a datetime (pandas parsed it)
    if isinstance(value, (datetime, pd.Timestamp)):
        dt = value.to_pydatetime() if isinstance(value, pd.Timestamp) else value
        if dt.tzinfo is None:
            dt = dj_timezone.make_aware(dt)
        return dt

    # String — try common formats
    value_str = str(value).strip()
    if not value_str:
        return None

    for fmt in ['%d-%m-%Y %H:%M', '%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y %H:%M', '%d-%m-%Y', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(value_str, fmt)
            return dj_timezone.make_aware(dt)
        except ValueError:
            continue

    logger.warning(f"Kon datetime niet parsen: {value}")
    return None


def parse_excel_date(value) -> Optional[date]:
    """
    Parse datum uit Excel. Handles pandas Timestamp, string, and NaT.

    Args:
        value: Waarde uit Excel kolom

    Returns:
        date object of None
    """
    if pd.isna(value):
        return None

    # Already a datetime/Timestamp
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.date() if isinstance(value, pd.Timestamp) else value.date()

    if isinstance(value, date):
        return value

    # String — use existing parser (DD-MM-YYYY)
    return parse_date_value(str(value).strip())


def clean_cell_value(value) -> Optional[str]:
    """
    Clean een Excel cel waarde naar string of None.

    Args:
        value: Ruwe cel waarde

    Returns:
        Getrimde string of None
    """
    if pd.isna(value):
        return None

    value_str = str(value).strip()

    if not value_str or value_str in ['- Maak een keuze -', 'nan', 'NaN', 'None']:
        return None

    return value_str


def transform_excel_row_to_input(
    row: pd.Series,
    row_index: int,
    column_map: dict
) -> Optional[AdviesAanvraagInput]:
    """
    Transformeer een Excel rij naar AdviesAanvraagInput.

    Mirrors transform_egrip_result_to_input from api_egrip.py.

    Args:
        row: Pandas Series (één rij)
        row_index: Rij nummer (voor logging)
        column_map: Mapping van Excel kolom → model veld

    Returns:
        Validated AdviesAanvraagInput of None bij fout
    """
    try:
        # Extract email (REQUIRED)
        email = clean_cell_value(row.get('E-mail'))
        if not email:
            logger.warning(f"Rij {row_index}: Geen email, skip")
            return None

        # Parse ingediend_op
        ingediend_op = parse_excel_datetime(row.get('Datum/tijd'))
        if not ingediend_op:
            ingediend_op = datetime.now()
            logger.warning(f"Rij {row_index}: Geen datum/tijd, gebruik huidige tijd")

        # Generate synthetic external_result_id
        external_id = generate_external_id(email, str(ingediend_op))

        # Build input data dictionary (same structure as api_egrip.py)
        input_data = {
            'external_result_id': external_id,
            'form_id': 'excel-1',
            'email': email,
            'ingediend_op': ingediend_op,
        }

        # Map all Excel columns to fields
        for excel_col, field_name in column_map.items():
            if excel_col not in row.index:
                continue

            value = row[excel_col]

            # Skip empty values
            cleaned = clean_cell_value(value)
            if cleaned is None:
                continue

            # Special handling for date fields
            if field_name in EXCEL_DATE_FIELDS:
                parsed_date = parse_excel_date(value)
                if parsed_date is not None:
                    input_data[field_name] = parsed_date
                continue

            # Special handling for boolean fields
            if field_name in BOOLEAN_FIELDS:
                parsed_bool = parse_boolean_value(cleaned)
                if parsed_bool is not None:
                    input_data[field_name] = parsed_bool
                continue

            # Don't overwrite already-set metadata fields
            if field_name in ('ingediend_op', 'email'):
                continue

            # Store string value (skip if already set by an earlier column)
            if field_name not in input_data:
                input_data[field_name] = cleaned

        # Validate with Pydantic (same as api_egrip.py)
        try:
            validated_input = AdviesAanvraagInput(**input_data)
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

def save_excel_aanvraag(
    validated_input: 'AdviesAanvraagInput',
    dry_run: bool = False
) -> Optional[AdviesAanvragen]:
    """
    Sla één Excel AdviesAanvraag op met extra dedup op email + ingediend_op.

    Checks both external_result_id (for re-running Excel import) and
    email + ingediend_op (for overlap with existing E-grip entries).
    """
    try:
        result_id = validated_input.external_result_id

        # Check 1: exact same Excel row already imported
        if AdviesAanvragen.objects.filter(external_result_id=result_id).exists():
            logger.debug(f"Result {result_id} al geïmporteerd (exact ID match), skip")
            return None

        # Check 2: same email + submission date already exists (e.g. from E-grip)
        # Compare date-only to handle timezone/precision differences
        if validated_input.ingediend_op and validated_input.email:
            submit_date = validated_input.ingediend_op.date()
            if AdviesAanvragen.objects.filter(
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
            aanvraag = AdviesAanvragen.objects.create(**aanvraag_data)

            naam = f"{aanvraag.voorletters_roepnaam or ''} {aanvraag.achternaam or ''}".strip()
            logger.info(f"✓ Aanvraag {result_id} opgeslagen: {naam} ({validated_input.email})")
            return aanvraag

    except Exception as e:
        logger.error(f"✗ Fout bij opslaan aanvraag {validated_input.external_result_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ============================================================================
# MAIN SYNC FUNCTION
# ============================================================================

def sync_excel_aanvragen(
    file_path: str,
    max_results: Optional[int] = None,
    dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Importeer AdviesAanvragen vanuit Excel bestand.

    Mirrors sync_egrip_formulieren from api_egrip.py.

    Args:
        file_path: Pad naar het Excel bestand
        max_results: Maximaal aantal rijen (voor testen), None = alle
        dry_run: If True, don't actually save to database

    Returns:
        Tuple van (success_count, error_count, skipped_count)
    """
    logger.info(f"=== Start Excel import van {file_path} {'(DRY RUN)' if dry_run else ''} ===")

    # Read Excel
    df = read_excel_aanvragen(file_path)

    if df is None:
        logger.error("Kon Excel bestand niet lezen")
        return 0, 1, 0

    if df.empty:
        logger.warning("Excel bestand is leeg")
        return 0, 0, 0

    # Check for required column
    if 'E-mail' not in df.columns:
        logger.error(f"Kolom 'E-mail' niet gevonden. Beschikbare kolommen: {list(df.columns)}")
        return 0, 1, 0

    # Log unmapped columns for debugging
    mapped_cols = set(EXCEL_COLUMN_MAP.keys())
    actual_cols = set(df.columns)
    unmapped = actual_cols - mapped_cols - SKIP_COLUMNS
    if unmapped:
        logger.info(f"Ongemapte kolommen (worden geskipt): {unmapped}")

    # Limit for testing
    if max_results:
        df = df.head(max_results)
        logger.info(f"TEST MODE: Verwerk alleen eerste {max_results} rijen")

    success_count = 0
    error_count = 0
    skipped_count = 0

    def process_rows():
        nonlocal success_count, error_count, skipped_count

        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel row number (1-indexed + header)
            logger.debug(f"Verwerk rij {row_num}")

            # Transform to validated input
            validated_input = transform_excel_row_to_input(
                row, row_num, EXCEL_COLUMN_MAP
            )

            if not validated_input:
                error_count += 1
                continue

            # Save to database (with email + ingediend_op dedup)
            aanvraag = save_excel_aanvraag(validated_input, dry_run=dry_run)

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

    logger.info(f"=== Excel import compleet: {success_count} succesvol, {skipped_count} geskipt, {error_count} fouten ===")
    return success_count, error_count, skipped_count
