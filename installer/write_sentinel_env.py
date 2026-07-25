"""Create or repair sentinel-auth's .env (always SQLite - see comment
below), and print the resulting SENTINEL_CLIENT_KEY on stdout so the
caller can capture it.

Usage: write_sentinel_env.py <sentinel_dir> <port>
"""
import secrets
import sys
import uuid
from pathlib import Path

sentinel_dir = Path(sys.argv[1])
port = sys.argv[2]
env_path = sentinel_dir / ".env"

# sentinel-auth's own storage is intentionally NOT the jdk MySQL database -
# it's a separate decoupled service, and AuthorizationService._dialect_insert
# has no MySQL write branch (reads like /api/roles work, writes 500). SQLite
# needs no server or credentials, so that's what this always configures.
if not env_path.exists():
    lines = [
        "SENTINEL_DATABASE_TYPE=sqlite",
        "SENTINEL_SQLITE_PATH=./sentinel.sqlite3",
        f"SENTINEL_JWT_SECRET_KEY={secrets.token_urlsafe(48)}",
        "SENTINEL_SERVER_HOST=127.0.0.1",
        f"SENTINEL_SERVER_PORT={port}",
        "SENTINEL_ALLOW_CORS=true",
        "SENTINEL_CORS_ORIGINS=http://localhost:5173",
        "SENTINEL_DEBUG_MODE=false",
        f"SENTINEL_CLIENT_KEY={uuid.uuid4()}",
    ]
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
else:
    lines = env_path.read_text(encoding="utf-8").splitlines()
    if any(l.startswith("SENTINEL_DATABASE_TYPE=mysql") for l in lines):
        lines = [
            l for l in lines
            if not l.startswith(("SENTINEL_DATABASE_TYPE=", "SENTINEL_MYSQL_URL=", "SENTINEL_SQLITE_PATH="))
        ]
        lines[:0] = ["SENTINEL_DATABASE_TYPE=sqlite", "SENTINEL_SQLITE_PATH=./sentinel.sqlite3"]
    if not any(l.startswith("SENTINEL_CLIENT_KEY=") for l in lines):
        lines.append(f"SENTINEL_CLIENT_KEY={uuid.uuid4()}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

client_key = next(
    l.split("=", 1)[1].strip() for l in env_path.read_text(encoding="utf-8").splitlines()
    if l.startswith("SENTINEL_CLIENT_KEY=")
)
# No trailing newline: cmd's `for /f` on Windows captures this script's
# stdout including a stray \r if we print() a line ending, which then gets
# baked into the UUID the caller writes into jdkv2's .env.
sys.stdout.write(client_key)
