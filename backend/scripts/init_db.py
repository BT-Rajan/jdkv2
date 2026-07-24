"""
Initialize the JDK database.

Applies, in dependency order:
  1. perennia-auth schema      (identity)
  2. perennia-access schema    (roles/permissions)
  3. perennia-search schema    (search index)
  4. perennia-notify schema    (notifications)
  5. perennia-files schema     (file storage)
  6. JDK's own schema          (backend/sql/schema.sql)
Then seeds JDK's permission/role vocabulary into perennia-access.

Usage (from backend/, with the virtualenv active and .env configured):

    python scripts/init_db.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.resources
import pymysql

from app.core.config import load_settings
from app.permissions import definitions as permission_definitions
from perennia_access import PerenniaAccess, AccessConfig, DatabaseConfig as AccessDatabaseConfig


def _read_package_schema(package: str) -> str:
    return importlib.resources.files(package).joinpath("schema.sql").read_text(encoding="utf-8")


def _apply(cur, sql: str) -> None:
    # naive split on ';' at statement boundaries - fine for these schema files
    # (no stored procedures / triggers containing embedded semicolons).
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            cur.execute(statement)


def main() -> None:
    settings = load_settings()

    conn = pymysql.connect(
        host=settings.db_host, port=settings.db_port,
        user=settings.db_user, password=settings.db_password,
        charset="utf8mb4", autocommit=True,
    )
    with conn.cursor() as cur:
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{settings.db_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    conn.select_db(settings.db_name)

    schemas = [
        ("perennia_auth", "perennia-auth"),
        ("perennia_access", "perennia-access"),
        ("perennia_search", "perennia-search"),
        ("perennia_notify", "perennia-notify"),
        ("perennia_files", "perennia-files"),
    ]
    with conn.cursor() as cur:
        for package, label in schemas:
            print(f"Applying {label} schema...")
            _apply(cur, _read_package_schema(package))

        print("Applying JDK schema...")
        jdk_schema = (Path(__file__).resolve().parent.parent / "sql" / "schema.sql").read_text(encoding="utf-8")
        _apply(cur, jdk_schema)

    conn.close()

    access = PerenniaAccess(
        AccessConfig(
            database=AccessDatabaseConfig(
                host=settings.db_host, port=settings.db_port, user=settings.db_user,
                password=settings.db_password, database=settings.db_name,
            )
        )
    )
    print("Seeding JDK permission/role vocabulary...")
    permission_definitions.seed(access)

    print("Done.")


if __name__ == "__main__":
    main()
