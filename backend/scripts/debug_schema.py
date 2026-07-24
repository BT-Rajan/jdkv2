"""
Step through a schema file one SQL statement at a time against the real
database, so a failure points at the exact statement and exact server
error instead of a wall of DDL.

Usage (from backend/, with the virtualenv active and .env configured):

    python scripts/debug_schema.py                  # step through all 6 schemas
    python scripts/debug_schema.py --only jdk        # step through just one
    python scripts/debug_schema.py --auto            # no pausing, just trace + stop on error
    python scripts/debug_schema.py --only jdk --from 12   # resume from statement #12

Per statement you get:
    [Enter]  run it
    s        skip it (mark as skipped, move on)
    a        abort (stop immediately, no more statements run)
    q        quit without running the rest (same as abort)
"""
import argparse
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pymysql

from app.core.config import load_settings
import init_db  # reuse the exact same splitter/comment-handling as the real installer

SCHEMAS = [
    ("perennia_auth", "perennia-auth"),
    ("perennia_access", "perennia-access"),
    ("perennia_search", "perennia-search"),
    ("perennia_notify", "perennia-notify"),
    ("perennia_files", "perennia-files"),
    (None, "jdk"),  # backend/sql/schema.sql, read separately below
]


def _schema_sql(package: str, label: str) -> str:
    if label == "jdk":
        return (Path(__file__).resolve().parent.parent / "sql" / "schema.sql").read_text(encoding="utf-8")
    return init_db._read_package_schema(package)


def _connect_to_target_db():
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
    return conn, settings.db_name


def _step_through(cur, label: str, statements: list, auto: bool, start_at: int) -> bool:
    """Returns True if this schema finished (possibly with skips), False if aborted."""
    total = len(statements)
    print(f"\n=== {label}: {total} statement(s) ===")
    for n, statement in enumerate(statements, start=1):
        if n < start_at:
            continue

        preview = " ".join(statement.split())[:100]
        print(f"\n[{label} {n}/{total}] {preview}...")

        if not auto:
            choice = input("  run? [Enter=run / s=skip / a=abort] ").strip().lower()
            if choice in ("a", "q"):
                print(f"  aborted at statement {n}/{total}.")
                return False
            if choice == "s":
                print("  skipped.")
                continue

        try:
            cur.execute(statement)
            print(f"  OK.")
        except pymysql.err.OperationalError as exc:
            errno = exc.args[0] if exc.args else None
            if errno in init_db._SKIPPABLE_ERRNOS:
                print(f"  already applied (errno {errno}), skipping.")
                continue
            print(f"  FAILED (errno {errno}): {exc.args[1] if len(exc.args) > 1 else exc}")
            print(f"  full statement:\n    " + "\n    ".join(statement.splitlines()))
            if auto:
                return False
            choice = input("  [Enter/r]=retry same statement, s=skip, a=abort ").strip().lower()
            if choice in ("a", "q", ""):
                return False
            if choice == "s":
                continue
        except Exception as exc:
            print(f"  FAILED: {exc}")
            print(f"  full statement:\n    " + "\n    ".join(statement.splitlines()))
            return False
    print(f"  [{label}] done.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Step through JDK's schemas one statement at a time.")
    parser.add_argument("--only", choices=[l for _, l in SCHEMAS], help="Debug just this one schema.")
    parser.add_argument("--auto", action="store_true", help="Don't pause between statements; stop on first error.")
    parser.add_argument("--from", dest="start_at", type=int, default=1, help="Resume from this statement number (1-based).")
    args = parser.parse_args()

    targets = [(p, l) for p, l in SCHEMAS if (args.only is None or l == args.only)]

    conn, db_name = _connect_to_target_db()
    print(f"Connected to `{db_name}`.")

    with conn.cursor() as cur:
        for package, label in targets:
            sql = _schema_sql(package, label)
            statements = [s.strip() for s in init_db._split_statements(sql)]
            statements = [s for s in statements if s and init_db._has_executable_sql(s)]
            ok = _step_through(cur, label, statements, args.auto, args.start_at if label == args.only else 1)
            if not ok:
                print(f"\nStopped during {label}. Nothing after this point was applied.")
                conn.close()
                sys.exit(1)

    conn.close()
    print("\nAll selected schemas stepped through successfully.")


if __name__ == "__main__":
    main()
