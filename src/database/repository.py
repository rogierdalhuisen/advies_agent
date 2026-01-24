"""Repository for AdviesAanvragen queries."""

from src.database.connection import get_cursor

TABLE = "adviesaanvragen"

# Full field mapping: position -> field_name
FIELD_MAP = {
    20: 'advies_voor_mezelf',
    50: 'aanhef',
    60: 'voorletters_roepnaam',
    70: 'achternaam',
    80: 'geboortedatum',
    90: 'land_nationaliteit',
    100: 'email',
    110: 'telefoonnummer',
    120: 'vaste_woonplaats',
    130: 'geen_vaste_woonplaats',
    140: 'meerdere_verzekerden',
    141: 'partner_naam',
    142: 'partner_geboortedatum',
    143: 'partner_nationaliteit',
    144: 'kind1_naam',
    145: 'kind1_geboortedatum',
    146: 'kind1_nationaliteit',
    147: 'kind2_naam',
    148: 'kind2_geboortedatum',
    149: 'kind2_nationaliteit',
    150: 'kind3_naam',
    151: 'kind3_geboortedatum',
    152: 'kind3_nationaliteit',
    153: 'kind4_naam',
    154: 'kind4_geboortedatum',
    155: 'kind4_nationaliteit',
    159: 'anders_personen',
    165: 'situatie_type',
    170: 'bestemming_land',
    175: 'vertrekdatum',
    220: 'uitschrijven_brp',
    225: 'huidig_woonland',
    230: 'advies_voor',
    240: 'hoofdreden_verblijf',
    245: 'toelichting_hoofdreden',
    247: 'verwachte_duur_verblijf',
    248: 'toelichting_duur',
    250: 'werk_omschrijving',
    260: 'plannen_omschrijving',
    270: 'salaris_uit_nederland',
    280: 'interesse_aov',
    290: 'loondienst_of_zelfstandig',
    300: 'eigen_onderneming_3jaar',
    310: 'bruto_jaarinkomen',
    320: 'aov_geen_offerte_reden',
    330: 'loon_doorbetaald_bij_ziekte',
    340: 'toelichting_uitkering',
    350: 'bruto_salaris_inkomen',
    360: 'salaris_per_maand_jaar',
    370: 'bouwplaats_of_offshore',
    380: 'bouwplaats_hoe_vaak',
    390: 'gevaarlijke_stoffen',
    400: 'toelichting_gevaarlijke_stoffen',
    411: 'interesse_internationale_aov',
    412: 'geen_interesse_aov_reden',
    413: 'functieomschrijving',
    414: 'type_werkzaamheden',
    415: 'verwacht_inkomen',
    416: 'inkomen_toelichting',
    419: 'interesse_zkv',
    420: 'zkv_geen_interesse_reden',
    430: 'zkv_dekkingsvariant',
    440: 'zkv_eigen_risico_voorkeur',
    450: 'zkv_eigen_risico_bedrag',
    460: 'zkv_periode',
    470: 'zkv_periode_omschrijving_motivatie',
    480: 'zkv_periode_omschrijving',
    490: 'huidige_verzekeraar',
    500: 'voorkeur_verzekeraar',
    510: 'medische_bijzonderheden',
    520: 'medische_bijzonderheden_toelichting',
    530: 'specifieke_wensen_zkv',
    540: 'wensen_toelichting',
    550: 'dekking_zwangerschap',
    560: 'zwangerschap_toelichting',
    565: 'andere_verzekeringen_interesse',
    566: 'overlijdensrisico_bedrag',
    567: 'overlijdensrisico_bedrag_anders',
    568: 'overlijdensrisico_bestemming',
    569: 'overlijdensrisico_bestemming_anders',
    580: 'sporten_activiteiten',
    590: 'sport_semiprofessioneel',
    600: 'sport_professioneel_omschrijving',
    660: 'huis_in_nederland',
    670: 'huis_type',
    680: 'woning_verhuurd',
    690: 'woning_eigen_gebruik',
    700: 'woning_verblijf_frequentie',
    710: 'woning_opmerkingen',
    740: 'hoe_gevonden',
    750: 'welke_website',
    760: 'naam_werkgever',
    770: 'hoe_gevonden_overig',
    780: 'eerder_contact_joho',
    790: 'eerder_contact_keuze',
    800: 'naam_contactpersoon',
    810: 'eerder_contact_anders',
    820: 'advies_vorm',
}

# Positions to extract - edit this list to change which fields are pulled
EXTRACT_POSITIONS = [
    80, 90, 142, 145, 148, 151, 154, 170, 175, 240, 245, 247, 248,
    411, 413, 414, 419, 430, 440, 450, 460, 470, 490, 500, 510, 520,
    530, 540, 550, 560, 580, 590, 600, 780, 790, 820
]

# Always include these columns
BASE_COLUMNS = ['aanvraag_id', 'email', 'ingediend_op']


def get_columns() -> str:
    """Get SQL column list based on EXTRACT_POSITIONS."""
    fields = [FIELD_MAP[pos] for pos in EXTRACT_POSITIONS if pos in FIELD_MAP]
    all_cols = BASE_COLUMNS + fields
    return ', '.join(all_cols)


def _fetch(query: str, params: tuple = ()) -> list[dict]:
    """Execute query and return results as list of dicts."""
    conn, cur = get_cursor()
    try:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_all() -> list[dict]:
    """Get all aanvragen with selected fields."""
    cols = get_columns()
    return _fetch(f"SELECT {cols} FROM {TABLE} ORDER BY ingediend_op DESC")


def get_recent_24h() -> list[dict]:
    """Get aanvragen from last 24 hours with selected fields."""
    cols = get_columns()
    return _fetch(
        f"SELECT {cols} FROM {TABLE} WHERE ingediend_op >= NOW() - INTERVAL '24 hours' ORDER BY ingediend_op DESC"
    )


def get_by_email(email: str) -> list[dict]:
    """Get aanvragen by email with selected fields."""
    cols = get_columns()
    return _fetch(f"SELECT {cols} FROM {TABLE} WHERE email = %s ORDER BY ingediend_op DESC", (email,))
