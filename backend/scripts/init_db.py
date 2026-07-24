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

Safe to re-run: statements that fail because the table/index/constraint
already exists (e.g. perennia-files' `ALTER TABLE files ADD CONSTRAINT
fk_files_current_version ...`, which has no IF NOT EXISTS guard) are
skipped rather than aborting the run.

Usage (from backend/, with the virtualenv active and .env configured):

    python scripts/init_db.py            # apply/upgrade in place
    python scripts/init_db.py --clean    # drop the database first, then build fresh
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.resources
import pymysql

from app.core.config import load_settings
from app.permissions import definitions as permission_definitions
from perennia_access import PerenniaAccess, AccessConfig, DatabaseConfig as AccessDatabaseConfig

# MySQL/MariaDB errnos meaning "this table/index/constraint already exists" -
# harmless to skip when re-applying schemas against a partially-initialized
# database. 121 is the InnoDB "duplicate key on write or update" errno that
# surfaces when an ALTER TABLE ADD CONSTRAINT is re-run.
_ALREADY_EXISTS_ERRNOS = {1005, 1022, 1050, 1061, 1826, 121}


def _read_package_schema(package: str) -> str:
    return importlib.resources.files(package).joinpath("schema.sql").read_text(encoding="utf-8")


def _apply(cur, sql: str, label: str) -> None:
    for statement in sql.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        try:
            cur.execute(statement)
        except pymysql.err.OperationalError as exc:
            errno = exc.args[0] if exc.args else None
            if errno in _ALREADY_EXISTS_ERRNOS:
                first_line = statement.splitlines()[0][:70]
                print(f"  [{label}] already applied, skipping: {first_line}...")
                continue
            raise


def run(clean: bool = False) -> None:
    settings = load_settings()

    conn = pymysql.connect(
        host=settings.db_host, port=settings.db_port,
        user=settings.db_user, password=settings.db_password,
        charset="utf8mb4", autocommit=True,
    )
    with conn.cursor() as cur:
        if clean:
            print(f"Dropping database `{settings.db_name}` (clean install)...")
            cur.execute(f"DROP DATABASE IF EXISTS `{settings.db_name}`")
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
            _apply(cur, _read_package_schema(package), label)

        print("Applying JDK schema...")
        jdk_schema = (Path(__file__).resolve().parent.parent / "sql" / "schema.sql").read_text(encoding="utf-8")
        _apply(cur, jdk_schema, "jdk")

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the JDK database.")
    parser.add_argument(
        "--clean", action="store_true",
        help="Drop the target database first for a fully fresh install.",
    )
    args = parser.parse_args()
    run(clean=args.clean)


if __name__ == "__main__":
    main()
