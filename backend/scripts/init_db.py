"""
Initialize the JDK database.

Applies, in dependency order:
  1. perennia-auth schema      (identity)
  2. perennia-search schema    (search index)
  3. perennia-notify schema    (notifications)
  4. perennia-files schema     (file storage)
  5. JDK's own schema          (backend/sql/schema.sql)
Then seeds JDK's permission/role vocabulary into sentinel-auth (roles/
permissions now live in that service's own database, created by sentinel
itself on startup - see BT-Rajan/perennia-auth's sentinel/database.py -
so there is no schema.sql to apply here for it).

Safe to re-run: statements that fail because the table/index/constraint
already exists (e.g. perennia-files' `ALTER TABLE files ADD CONSTRAINT
fk_files_current_version ...`, which has no IF NOT EXISTS guard) are
skipped rather than aborting the run.

Usage (from backend/, with the virtualenv active and .env configured, and
the sentinel-auth service already running at SENTINEL_SERVICE_URL):

    python scripts/init_db.py            # apply/upgrade in place
    python scripts/init_db.py --clean    # drop the database first, then build fresh
"""
import argparse
import sys
from pathlib import Path

# On Windows, stdout redirected to a file (not a real console) falls back to
# the system ANSI codepage (commonly cp1252), which can't encode most
# non-ASCII characters. Force UTF-8 so logging never crashes on encoding.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.resources
import pymysql

from app.core.config import load_settings
from app.permissions import definitions as permission_definitions
from app.core.sentinel_access import SentinelAccess, AccessConfig

# MySQL/MariaDB errnos meaning "this table/index/constraint already exists" -
# harmless to skip when re-applying schemas against a partially-initialized
# database. 121 is the InnoDB "duplicate key on write or update" errno that
# surfaces when an ALTER TABLE ADD CONSTRAINT is re-run.
# 1054: unknown column - lets ALTER TABLE ... CHANGE COLUMN <old> <new>
# rename migrations be skipped on a fresh install, where schema.sql already
# creates the target column directly and <old> never existed.
_ALREADY_EXISTS_ERRNOS = {1005, 1022, 1050, 1054, 1060, 1061, 1826, 121}
# 1065: "Query was empty" - defensive fallback for a comment-only chunk
# slipping past _has_executable_sql.
_SKIPPABLE_ERRNOS = _ALREADY_EXISTS_ERRNOS | {1065}


def _read_package_schema(package: str) -> str:
    return importlib.resources.files(package).joinpath("schema.sql").read_text(encoding="utf-8")


def _split_statements(sql: str) -> list:
    """Split a .sql file into individual statements on ';', correctly
    ignoring semicolons that appear inside -- line comments, /* */ block
    comments, or quoted strings/identifiers (naive sql.split(";") breaks on
    e.g. "-- ...the bytes; it has no notion..." in a comment)."""
    statements = []
    buf = []
    i, n = 0, len(sql)
    in_line_comment = False
    in_block_comment = False
    quote_char = None  # one of ', ", ` while inside a quoted span

    while i < n:
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < n else ""

        if in_line_comment:
            buf.append(ch)
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue
        if in_block_comment:
            buf.append(ch)
            if ch == "*" and nxt == "/":
                buf.append(nxt)
                i += 2
                in_block_comment = False
                continue
            i += 1
            continue
        if quote_char:
            buf.append(ch)
            if ch == "\\":  # escaped char, consume it verbatim
                if nxt:
                    buf.append(nxt)
                    i += 2
                    continue
            elif ch == quote_char:
                quote_char = None
            i += 1
            continue

        # not currently inside any comment/quote
        if ch == "-" and nxt == "-":
            in_line_comment = True
            buf.append(ch)
            i += 1
            continue
        if ch == "#":
            in_line_comment = True
            buf.append(ch)
            i += 1
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            buf.append(ch)
            i += 1
            continue
        if ch in ("'", '"', "`"):
            quote_char = ch
            buf.append(ch)
            i += 1
            continue
        if ch == ";":
            statements.append("".join(buf))
            buf = []
            i += 1
            continue

        buf.append(ch)
        i += 1

    if buf:
        statements.append("".join(buf))
    return statements


def _has_executable_sql(statement: str) -> bool:
    """True if statement has any real SQL left once -- / # / block comments
    are stripped (a chunk that's comment-only would otherwise reach the
    server as an empty query and error with errno 1065)."""
    for line in statement.splitlines():
        line = line.split("--", 1)[0].split("#", 1)[0].strip()
        if line and not (line.startswith("/*") and line.endswith("*/")):
            return True
    return False


def _apply(cur, sql: str, label: str) -> None:
    statements = [s.strip() for s in _split_statements(sql)]
    statements = [s for s in statements if s and _has_executable_sql(s)]
    for n, statement in enumerate(statements, start=1):
        try:
            cur.execute(statement)
        except pymysql.err.OperationalError as exc:
            errno = exc.args[0] if exc.args else None
            if errno in _SKIPPABLE_ERRNOS:
                first_line = statement.splitlines()[0][:70]
                print(f"  [{label}] already applied, skipping: {first_line}...")
                continue
            raise
        except Exception:
            print(f"  [{label}] FAILED on statement {n}/{len(statements)}:")
            print("  " + "\n  ".join(statement.splitlines()[:8]))
            raise
    print(f"  [{label}] {len(statements)} statement(s) applied successfully.")


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
        ("perennia_search", "perennia-search"),
        ("perennia_notify", "perennia-notify"),
        ("perennia_files", "perennia-files"),
    ]
    with conn.cursor() as cur:
        for package, label in schemas:
            print(f"Applying {label} schema...")
            _apply(cur, _read_package_schema(package), label)
            print(f"[OK] {label} schema applied successfully.\n")

        print("Applying JDK schema...")
        jdk_schema = (Path(__file__).resolve().parent.parent / "sql" / "schema.sql").read_text(encoding="utf-8")
        _apply(cur, jdk_schema, "jdk")
        print("[OK] JDK schema applied successfully.\n")

        migrations_dir = Path(__file__).resolve().parent.parent / "sql" / "migrations"
        for migration_path in sorted(migrations_dir.glob("*.sql")):
            label = f"jdk:{migration_path.stem}"
            print(f"Applying {migration_path.name}...")
            _apply(cur, migration_path.read_text(encoding="utf-8"), label)
            print(f"[OK] {migration_path.name} applied successfully.\n")

    conn.close()

    access = SentinelAccess(
        AccessConfig(
            service_url=settings.sentinel_service_url,
            client_key=settings.sentinel_client_key,
        )
    )
    print("Seeding JDK permission/role vocabulary into sentinel-auth...")
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
