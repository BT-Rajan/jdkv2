"""
JDK's own database connection helper.

This connects to the same MySQL database that perennia-auth, perennia-access,
perennia-search, perennia-notify and perennia-files use, but is a completely
separate connection object owned by JDK. JDK never reaches into another
package's tables to write - only to read identity/session-shape data it needs
to display (e.g. joining `auth_identifiers.email` into a user search result).
All writes to perennia-owned tables go through that package's public API.
"""
from contextlib import contextmanager

import pymysql
import pymysql.cursors

from app.core.config import Settings


class Database:
    """Thin connection/transaction wrapper for JDK's own business tables."""

    def __init__(self, settings: Settings):
        self._settings = settings

    def _connect(self):
        return pymysql.connect(
            host=self._settings.db_host,
            port=self._settings.db_port,
            user=self._settings.db_user,
            password=self._settings.db_password,
            database=self._settings.db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    @contextmanager
    def transaction(self):
        """Yields a cursor. Commits on success, rolls back on any exception."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def cursor(self):
        """Read-only convenience cursor."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            yield cur
        finally:
            conn.close()
