"""
Django management command to import AdviesAanvragen from Excel.

Usage:
    python manage.py import_excel_aanvragen /path/to/aanvragen.xlsx
    python manage.py import_excel_aanvragen /path/to/aanvragen.xlsx --dry-run
    python manage.py import_excel_aanvragen /path/to/aanvragen.xlsx --max-results 5
"""

from django.core.management.base import BaseCommand, CommandError
from comparator_app.api_excel import sync_excel_aanvragen


class Command(BaseCommand):
    help = 'Importeert AdviesAanvragen vanuit een Excel bestand (oude formulieren).'

    def add_arguments(self, parser):
        """Voeg command-line argumenten toe."""

        parser.add_argument(
            'excel_file',
            type=str,
            help='Pad naar het Excel bestand met aanvragen'
        )

        parser.add_argument(
            '--max-results',
            type=int,
            default=None,
            help='Maximaal aantal rijen om te verwerken (voor testen)'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without committing to database (DRY RUN mode)'
        )

    def handle(self, *args, **options):
        """Voer de import uit."""

        excel_file = options['excel_file']
        max_results = options['max_results']
        dry_run = options['dry_run']

        # Header
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("  EXCEL AANVRAGEN IMPORT"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        # Configuratie
        self.stdout.write("Configuratie:")
        self.stdout.write(f"  - Bestand: {excel_file}")
        if max_results:
            self.stdout.write(f"  - Max rijen: {max_results} (TEST MODE)")
        else:
            self.stdout.write(f"  - Max rijen: Alle")

        if dry_run:
            self.stdout.write(self.style.WARNING(f"  - DRY RUN: Enabled (geen wijzigingen worden opgeslagen)"))
        else:
            self.stdout.write(f"  - DRY RUN: Disabled (wijzigingen worden opgeslagen)")
        self.stdout.write("")

        # Dry run warning
        if dry_run:
            self.stdout.write(self.style.WARNING("⚠ DRY RUN MODE: Geen data wordt opgeslagen in de database"))
            self.stdout.write("")

        # Import
        self.stdout.write(self.style.WARNING(">>> IMPORTEREN EXCEL AANVRAGEN"))
        self.stdout.write("")

        try:
            success, errors, skipped = sync_excel_aanvragen(
                file_path=excel_file,
                max_results=max_results,
                dry_run=dry_run
            )

            self.stdout.write("")
            if dry_run:
                self.stdout.write(self.style.SUCCESS(f"✓ Excel DRY RUN voltooid!"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✓ Excel import voltooid!"))

            self.stdout.write(f"  - Succesvol: {success}")
            self.stdout.write(f"  - Geskipt (duplicaten): {skipped}")
            self.stdout.write(f"  - Fouten: {errors}")
            self.stdout.write("")

            if errors > 0:
                self.stdout.write(self.style.WARNING(f"⚠ Let op: {errors} fouten tijdens import. Check de logs."))
                self.stdout.write("")

            if dry_run:
                self.stdout.write(self.style.NOTICE("ℹ Dit was een DRY RUN. Voer het commando zonder --dry-run uit om wijzigingen op te slaan."))
                self.stdout.write("")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ FOUT bij Excel import: {e}"))
            self.stdout.write("")
            import traceback
            self.stdout.write(traceback.format_exc())
            return

        # Footer
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("  IMPORT COMPLEET"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
