"""Upsert connection/secret values into jdkv2's .env without disturbing
the rest of the file. Secrets/DB_* are only filled in if not already
set, so re-runs don't rotate them.

Usage: upsert_jdk_env.py <jdk_dir> <sentinel_port> <sentinel_client_key>
"""
import secrets
import sys
from pathlib import Path

jdk_dir = Path(sys.argv[1])
sentinel_port = sys.argv[2]
client_key = sys.argv[3].strip()
env_path = jdk_dir / ".env"

lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
existing = {}
for line in lines:
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        existing[k] = v.strip()

always_set = {
    "SENTINEL_SERVICE_URL": f"http://127.0.0.1:{sentinel_port}",
    "SENTINEL_CLIENT_KEY": client_key,
}
fill_if_empty = {
    "DB_HOST": "localhost",
    "DB_PORT": "3306",
    "DB_USER": "root",
    "DB_NAME": "jdk",
    "AUTH_SIGNING_SECRET": secrets.token_urlsafe(48),
    "FILES_SIGNING_SECRET": secrets.token_urlsafe(48),
    "FILES_STORAGE_PATH": "./var/files",
    "ENVIRONMENT": "development",
    "CORS_ORIGINS": "http://localhost:5173",
}

values = dict(always_set)
for k, v in fill_if_empty.items():
    if not existing.get(k):
        values[k] = v

seen = set()
out = []
for line in lines:
    key = line.split("=", 1)[0] if "=" in line and not line.strip().startswith("#") else None
    if key in values:
        out.append(f"{key}={values[key]}")
        seen.add(key)
    else:
        out.append(line)
for key, val in values.items():
    if key not in seen:
        out.append(f"{key}={val}")

env_path.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"[OK] wrote {env_path}")
