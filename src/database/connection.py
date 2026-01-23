"""PostgreSQL database connection management."""

import logging
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from src.config import get_postgres_url, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL database connections."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.host = host or POSTGRES_HOST
        self.port = port or POSTGRES_PORT
        self.database = database or POSTGRES_DB
        self.user = user or POSTGRES_USER
        self.password = password or POSTGRES_PASSWORD
        self._connection = None

    def connect(self) -> psycopg2.extensions.connection:
        """Create a new database connection."""
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                )
                logger.info(f"Connected to PostgreSQL at {self.host}:{self.port}/{self.database}")
            except psycopg2.Error as e:
                logger.error(f"Failed to connect to PostgreSQL: {e}")
                raise
        return self._connection

    def close(self):
        """Close the database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("Closed PostgreSQL connection")

    @contextmanager
    def cursor(self, dict_cursor: bool = True) -> Generator:
        """Context manager for database cursors.

        Args:
            dict_cursor: If True, return results as dictionaries.

        Yields:
            Database cursor.
        """
        conn = self.connect()
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Singleton connection instance
_default_connection: Optional[DatabaseConnection] = None


def get_connection() -> DatabaseConnection:
    """Get the default database connection (singleton)."""
    global _default_connection
    if _default_connection is None:
        _default_connection = DatabaseConnection()
    return _default_connection
