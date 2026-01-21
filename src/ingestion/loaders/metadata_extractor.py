"""
Metadata extraction from file paths and content.

Extracts structured metadata from folder names, filenames, and document content.
"""

from pathlib import Path
from datetime import datetime
import re
import hashlib


class MetadataExtractor:
    """Extract metadata from file paths and content"""

    # Map folder names to human-readable display names
    COMPANY_DISPLAY_NAMES = {
        "ACS": "ACS International",
        "allianz_care": "Allianz Care",
        "allianz_globetrotter": "Allianz Globetrotter",
        "cigna_close_care": "Cigna Close Care",
        "cigna_global_care": "Cigna Global Care",
        "expatriate_group": "Expatriate Group",
        "globality_yougenio": "Globality Yougenio",
        "goudse_expat_pakket": "Goudse Expat Package",
        "goudse_ngo_zendelingen": "Goudse NGO Zendelingen",
        "goudse_working_nomad": "Goudse Working Nomad",
        "IMG_": "IMG (International Medical Group)",
        "International Expat Insurance": "International Expat Insurance",
        "MSH": "MSH International",
        "oom_tib": "OOM TIB",
        "oom_wib": "OOM WIB",
        "special_isis": "Special ISIS",
    }

    def extract_from_path(self, file_path: Path, base_dir: Path) -> dict:
        """
        Extract metadata from file path structure.

        Args:
            file_path: Full path to the document file
            base_dir: Base documents directory

        Returns:
            Dictionary with extracted metadata
        """
        # Get relative path from base directory
        relative_path = file_path.relative_to(base_dir)

        # Insurance provider is the first folder name
        insurance_provider = relative_path.parts[0]

        # Get human-readable display name
        company_display = self.COMPANY_DISPLAY_NAMES.get(
            insurance_provider, insurance_provider.replace("_", " ").title()
        )

        # Detect document type from filename
        filename = file_path.name

        # Extract version date from webpage files
        version_date = self._extract_version_date(filename)

        # Generate document ID (stable hash based on filepath)
        document_id = self._generate_document_id(str(file_path))

        metadata = {
            "insurance_provider": insurance_provider,
            "company_display_name": company_display,
            "document_name": filename,
            "version_date": version_date,
            "is_webpage": filename.startswith("webpage_"),
            "filepath": str(file_path),
            "document_id": document_id,
            "ingestion_timestamp": datetime.now().isoformat(),
        }
        return metadata

    def _extract_version_date(self, filename: str) -> str | None:
        """
        Extract date from webpage_YYYYMMDD.md format.

        Args:
            filename: Name of the file

        Returns:
            ISO format date string (YYYY-MM-DD) or None
        """
        match = re.search(r"webpage_(\d{8})\.md", filename)
        if match:
            date_str = match.group(1)
            # Convert to ISO format: YYYYMMDD -> YYYY-MM-DD
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        return None

    def _generate_document_id(self, filepath: str) -> str:
        """
        Generate a unique, stable document ID from filepath.

        Uses SHA-256 hash truncated to 16 characters for uniqueness.

        Args:
            filepath: Full path to the document

        Returns:
            Unique document identifier
        """
        return hashlib.sha256(filepath.encode()).hexdigest()[:16]

    def compute_content_hash(self, content: str) -> str:
        """
        Compute content hash for change detection.

        Args:
            content: Document content

        Returns:
            SHA-256 hash of content
        """
        return hashlib.sha256(content.encode()).hexdigest()
