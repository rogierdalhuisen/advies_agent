"""Repository for accessing AdviesAanvragen data."""

import logging
from typing import Optional

from src.database.connection import DatabaseConnection, get_connection
from src.database.models import AdviesAanvraag

logger = logging.getLogger(__name__)


class AdviesAanvragenRepository:
    """Repository for querying AdviesAanvragen from PostgreSQL."""

    TABLE_NAME = "adviesaanvragen"

    def __init__(self, connection: Optional[DatabaseConnection] = None):
        self.connection = connection or get_connection()

    def get_by_id(self, aanvraag_id: int) -> Optional[AdviesAanvraag]:
        """Fetch a single AdviesAanvraag by its ID.

        Args:
            aanvraag_id: The primary key of the aanvraag.

        Returns:
            AdviesAanvraag if found, None otherwise.
        """
        query = f"SELECT * FROM {self.TABLE_NAME} WHERE aanvraag_id = %s"

        with self.connection.cursor() as cursor:
            cursor.execute(query, (aanvraag_id,))
            row = cursor.fetchone()

        if row:
            return AdviesAanvraag.model_validate(dict(row))
        return None

    def get_by_email(self, email: str) -> list[AdviesAanvraag]:
        """Fetch all AdviesAanvragen for a given email address.

        Args:
            email: Email address to search for.

        Returns:
            List of matching AdviesAanvraag objects.
        """
        query = f"""
            SELECT * FROM {self.TABLE_NAME}
            WHERE email = %s
            ORDER BY ingediend_op DESC
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (email,))
            rows = cursor.fetchall()

        return [AdviesAanvraag.model_validate(dict(row)) for row in rows]

    def get_by_external_id(self, external_id: str) -> Optional[AdviesAanvraag]:
        """Fetch an AdviesAanvraag by its external result ID.

        Args:
            external_id: The external_result_id from the form system.

        Returns:
            AdviesAanvraag if found, None otherwise.
        """
        query = f"SELECT * FROM {self.TABLE_NAME} WHERE external_result_id = %s"

        with self.connection.cursor() as cursor:
            cursor.execute(query, (external_id,))
            row = cursor.fetchone()

        if row:
            return AdviesAanvraag.model_validate(dict(row))
        return None

    def get_recent(self, limit: int = 10) -> list[AdviesAanvraag]:
        """Fetch the most recent AdviesAanvragen.

        Args:
            limit: Maximum number of results to return.

        Returns:
            List of AdviesAanvraag objects ordered by submission date.
        """
        query = f"""
            SELECT * FROM {self.TABLE_NAME}
            ORDER BY ingediend_op DESC NULLS LAST
            LIMIT %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

        return [AdviesAanvraag.model_validate(dict(row)) for row in rows]

    def search(
        self,
        destination: Optional[str] = None,
        interested_zkv: Optional[bool] = None,
        interested_aov: Optional[bool] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 100,
    ) -> list[AdviesAanvraag]:
        """Search AdviesAanvragen with filters.

        Args:
            destination: Filter by destination country (bestemming_land).
            interested_zkv: Filter by health insurance interest.
            interested_aov: Filter by disability insurance interest.
            from_date: Filter by submission date (>=).
            to_date: Filter by submission date (<=).
            limit: Maximum number of results.

        Returns:
            List of matching AdviesAanvraag objects.
        """
        conditions = []
        params = []

        if destination:
            conditions.append("(bestemming_land ILIKE %s OR huidig_woonland ILIKE %s)")
            params.extend([f"%{destination}%", f"%{destination}%"])

        if interested_zkv is not None:
            if interested_zkv:
                conditions.append("interesse_zkv ILIKE %s")
                params.append("%ja%")
            else:
                conditions.append("(interesse_zkv IS NULL OR interesse_zkv NOT ILIKE %s)")
                params.append("%ja%")

        if interested_aov is not None:
            if interested_aov:
                conditions.append("interesse_aov ILIKE %s")
                params.append("%ja%")
            else:
                conditions.append("(interesse_aov IS NULL OR interesse_aov NOT ILIKE %s)")
                params.append("%ja%")

        if from_date:
            conditions.append("ingediend_op >= %s")
            params.append(from_date)

        if to_date:
            conditions.append("ingediend_op <= %s")
            params.append(to_date)

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        query = f"""
            SELECT * FROM {self.TABLE_NAME}
            WHERE {where_clause}
            ORDER BY ingediend_op DESC NULLS LAST
            LIMIT %s
        """
        params.append(limit)

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [AdviesAanvraag.model_validate(dict(row)) for row in rows]

    def count(self) -> int:
        """Get total count of AdviesAanvragen.

        Returns:
            Total number of records in the table.
        """
        query = f"SELECT COUNT(*) as count FROM {self.TABLE_NAME}"

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()

        return row["count"] if row else 0

    def get_statistics(self) -> dict:
        """Get basic statistics about the AdviesAanvragen.

        Returns:
            Dictionary with statistics.
        """
        query = f"""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN interesse_zkv ILIKE '%ja%' THEN 1 END) as zkv_interested,
                COUNT(CASE WHEN interesse_aov ILIKE '%ja%' THEN 1 END) as aov_interested,
                COUNT(DISTINCT bestemming_land) as unique_destinations,
                MIN(ingediend_op) as earliest,
                MAX(ingediend_op) as latest
            FROM {self.TABLE_NAME}
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()

        if row:
            return {
                "total_requests": row["total"],
                "zkv_interested": row["zkv_interested"],
                "aov_interested": row["aov_interested"],
                "unique_destinations": row["unique_destinations"],
                "date_range": {
                    "earliest": str(row["earliest"]) if row["earliest"] else None,
                    "latest": str(row["latest"]) if row["latest"] else None,
                },
            }
        return {}
