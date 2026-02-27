"""
Django management command to import AdviesAanvraagEngels from Excel.

Usage:
    python manage.py import_excel_engels /path/to/file.xlsx
    python manage.py import_excel_engels /path/to/file.xlsx --dry-run
    python manage.py import_excel_engels /path/to/file.xlsx --max-results 5
"""

from django.core.management.base import BaseCommand
from comparator_app.api_excel_engels import sync_excel_aanvragen_engels


class Command(BaseCommand):
    help = 'Import AdviesAanvraagEngels from an Excel file (English forms).'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Path to the Excel file'
        )
        parser.add_argument(
            '--max-results',
            type=int,
            default=None,
            help='Maximum number of rows to process (for testing)'
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
        self.stdout.write(self.style.SUCCESS("  EXCEL IMPORT - ADVIES AANVRAGEN (ENGELS)"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        self.stdout.write("Configuration:")
        self.stdout.write(f"  - File: {excel_file}")
        self.stdout.write(f"  - Max rows: {max_results or 'All'}")
        if dry_run:
            self.stdout.write(self.style.WARNING("  - DRY RUN: Enabled"))
        else:
            self.stdout.write("  - DRY RUN: Disabled")
        self.stdout.write("")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: No data will be saved"))
            self.stdout.write("")

        try:
            success, errors, skipped = sync_excel_aanvragen_engels(
                file_path=excel_file,
                max_results=max_results,
                dry_run=dry_run
            )

            self.stdout.write("")
            if dry_run:
                self.stdout.write(self.style.SUCCESS("DRY RUN complete!"))
            else:
                self.stdout.write(self.style.SUCCESS("Import complete!"))

            self.stdout.write(f"  - Success: {success}")
            self.stdout.write(f"  - Skipped (duplicates): {skipped}")
            self.stdout.write(f"  - Errors: {errors}")
            self.stdout.write("")

            if errors > 0:
                self.stdout.write(self.style.WARNING(f"Warning: {errors} errors during import. Check the logs."))

            if dry_run:
                self.stdout.write(self.style.NOTICE("Run without --dry-run to save changes."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERROR: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc())
            return

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("  IMPORT COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
