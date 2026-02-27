"""
Django management command to import AdviesAanvraagWoning from Excel.

Usage:
    python manage.py import_excel_woning /path/to/file.xlsx
    python manage.py import_excel_woning /path/to/file.xlsx --dry-run
    python manage.py import_excel_woning /path/to/file.xlsx --max-results 5
"""

from django.core.management.base import BaseCommand
from comparator_app.api_excel_woning import sync_excel_aanvragen_woning


class Command(BaseCommand):
    help = 'Importeert AdviesAanvraagWoning vanuit een Excel bestand (woningformulieren).'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Pad naar het Excel bestand'
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
            help='Preview changes without committing to database'
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        max_results = options['max_results']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("  EXCEL IMPORT - ADVIES AANVRAGEN (WONING)"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        self.stdout.write("Configuratie:")
        self.stdout.write(f"  - Bestand: {excel_file}")
        self.stdout.write(f"  - Max rijen: {max_results or 'Alle'}")
        if dry_run:
            self.stdout.write(self.style.WARNING("  - DRY RUN: Enabled"))
        else:
            self.stdout.write("  - DRY RUN: Disabled")
        self.stdout.write("")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: Geen data wordt opgeslagen"))
            self.stdout.write("")

        try:
            success, errors, skipped = sync_excel_aanvragen_woning(
                file_path=excel_file,
                max_results=max_results,
                dry_run=dry_run
            )

            self.stdout.write("")
            if dry_run:
                self.stdout.write(self.style.SUCCESS("DRY RUN voltooid!"))
            else:
                self.stdout.write(self.style.SUCCESS("Import voltooid!"))

            self.stdout.write(f"  - Succesvol: {success}")
            self.stdout.write(f"  - Geskipt (duplicaten): {skipped}")
            self.stdout.write(f"  - Fouten: {errors}")
            self.stdout.write("")

            if errors > 0:
                self.stdout.write(self.style.WARNING(f"Let op: {errors} fouten tijdens import. Check de logs."))

            if dry_run:
                self.stdout.write(self.style.NOTICE("Voer het commando zonder --dry-run uit om wijzigingen op te slaan."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"FOUT: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc())
            return

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("  IMPORT COMPLEET"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
