"""
Django management command to analyze conversion rates from forms to contracts.

Usage:
    python manage.py analyze_conversions
    python manage.py analyze_conversions --period year
    python manage.py analyze_conversions --period month
    python manage.py analyze_conversions --form aanvragen
"""

from django.core.management.base import BaseCommand
from django.db import connection


FORM_QUERIES = {
    'adviesaanvragen': {
        'label': 'Advies Aanvragen (NL)',
        'table': 'adviesaanvragen',
        'date_field': 'ingediend_op',
        'name_fields': "a.voorletters_roepnaam || ' ' || a.achternaam",
    },
    'adviesaanvragen_engels': {
        'label': 'Advies Aanvragen (Engels)',
        'table': 'adviesaanvragen_engels',
        'date_field': 'ingediend_op',
        'name_fields': "a.voorletters_roepnaam || ' ' || a.achternaam",
    },
    'adviesaanvragen_belgie': {
        'label': 'Advies Aanvragen (België)',
        'table': 'adviesaanvragen_belgie',
        'date_field': 'ingediend_op',
        'name_fields': "a.voorletters_roepnaam || ' ' || a.achternaam",
    },
    'adviesaanvragen_woning': {
        'label': 'Advies Aanvragen (Woning)',
        'table': 'adviesaanvragen_woning',
        'date_field': 'ingediend_op',
        'name_fields': "a.voornaam || ' ' || a.achternaam",
    },
    'offertes_arbeidsongeschiktheid': {
        'label': 'Offertes Arbeidsongeschiktheid',
        'table': 'offertes_arbeidsongeschiktheid',
        'date_field': 'ingediend_op',
        'name_fields': "a.voorletters || ' ' || a.achternaam",
    },
    'allianz_care_quotes': {
        'label': 'Allianz Care Quotes',
        'table': 'allianz_care_quotes',
        'date_field': 'ingediend_op',
        'name_fields': "a.first_name || ' ' || a.last_name",
    },
}


def pct(num, denom):
    if denom == 0:
        return 0.0
    return round(100.0 * num / denom, 1)


class Command(BaseCommand):
    help = 'Analyseert conversieratio van formulieren naar contracten.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            choices=['month', 'year', 'none'],
            default='none',
            help='Groepeer op maand of jaar (default: alleen totalen)',
        )
        parser.add_argument(
            '--form',
            type=str,
            choices=list(FORM_QUERIES.keys()) + ['all'],
            default='all',
            help='Welk formulier analyseren (default: all)',
        )

    def handle(self, *args, **options):
        period = options['period']
        form_filter = options['form']

        forms = FORM_QUERIES if form_filter == 'all' else {form_filter: FORM_QUERIES[form_filter]}

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
        self.stdout.write(self.style.SUCCESS('  CONVERSIE-ANALYSE: Formulieren → Contracten'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        # Overall summary
        self._print_totals(forms)

        # Period breakdown
        if period != 'none':
            for key, config in forms.items():
                self._print_period_breakdown(config, period)

        self.stdout.write('')

    def _print_totals(self, forms):
        """Print total conversion for each form type."""
        self.stdout.write(self.style.MIGRATE_HEADING('\n  TOTALEN PER FORMULIER'))
        self.stdout.write('  ' + '-' * 76)
        self.stdout.write(
            f"  {'Formulier':<35} {'Aanvragen':>10} {'Met contract':>14} {'Conversie':>10}"
        )
        self.stdout.write('  ' + '-' * 76)

        grand_total_forms = 0
        grand_total_converted = 0

        with connection.cursor() as cursor:
            for key, config in forms.items():
                table = config['table']

                # Total forms
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_forms = cursor.fetchone()[0]

                # Forms with at least one contract (via relatie)
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT a.relatie_id)
                    FROM {table} a
                    INNER JOIN contracten c ON a.relatie_id = c.relatie_id
                """)
                converted = cursor.fetchone()[0]

                grand_total_forms += total_forms
                grand_total_converted += converted

                conv = pct(converted, total_forms)
                self.stdout.write(
                    f"  {config['label']:<35} {total_forms:>10} {converted:>14} {conv:>9.1f}%"
                )

        self.stdout.write('  ' + '-' * 76)
        grand_conv = pct(grand_total_converted, grand_total_forms)
        self.stdout.write(
            f"  {'TOTAAL':<35} {grand_total_forms:>10} {grand_total_converted:>14} {grand_conv:>9.1f}%"
        )

    def _print_period_breakdown(self, config, period):
        """Print conversion breakdown per month or year."""
        table = config['table']
        date_field = config['date_field']
        label = config['label']

        if period == 'month':
            trunc = f"TO_CHAR({date_field}, 'YYYY-MM')"
            period_label = 'Maand'
        else:
            trunc = f"TO_CHAR({date_field}, 'YYYY')"
            period_label = 'Jaar'

        self.stdout.write(self.style.MIGRATE_HEADING(f'\n  {label} — per {period_label.lower()}'))
        self.stdout.write('  ' + '-' * 76)
        self.stdout.write(
            f"  {period_label:<15} {'Aanvragen':>10} {'Met contract':>14} {'Conversie':>10} {'# Contracten':>14}"
        )
        self.stdout.write('  ' + '-' * 76)

        with connection.cursor() as cursor:
            # Total forms per period
            cursor.execute(f"""
                SELECT {trunc} AS periode, COUNT(*) AS total
                FROM {table}
                WHERE {date_field} IS NOT NULL
                GROUP BY {trunc}
                ORDER BY {trunc}
            """)
            totals_by_period = {row[0]: row[1] for row in cursor.fetchall()}

            # Converted (distinct relaties with contracts) per period
            cursor.execute(f"""
                SELECT {trunc} AS periode,
                       COUNT(DISTINCT a.relatie_id) AS converted,
                       COUNT(DISTINCT c.contract_id) AS num_contracts
                FROM {table} a
                INNER JOIN contracten c ON a.relatie_id = c.relatie_id
                WHERE a.{date_field} IS NOT NULL
                GROUP BY {trunc}
                ORDER BY {trunc}
            """)
            converted_by_period = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

            for periode in sorted(totals_by_period.keys()):
                total = totals_by_period[periode]
                converted, num_contracts = converted_by_period.get(periode, (0, 0))
                conv = pct(converted, total)
                self.stdout.write(
                    f"  {periode:<15} {total:>10} {converted:>14} {conv:>9.1f}% {num_contracts:>14}"
                )

            # Forms without a date
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table} WHERE {date_field} IS NULL
            """)
            no_date = cursor.fetchone()[0]
            if no_date > 0:
                self.stdout.write(self.style.WARNING(
                    f"  {'(geen datum)':<15} {no_date:>10}"
                ))
