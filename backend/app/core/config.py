"""
Application settings.

All configuration is read from environment variables (see .env.example at
the repository root). Nothing here is hardcoded secret data - only
structural defaults for local development.
"""
from dataclasses import dataclass
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

# Repository root .env (backend/app/core/config.py -> repo root is 3 levels up).
load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    # Single shared MySQL database. perennia-auth, perennia-access,
    # perennia-search, perennia-notify and perennia-files each run their own
    # schema.sql against this same database (see backend/scripts/init_db.py),
    # and JDK's own business tables (backend/sql/schema.sql) live alongside
    # them. This mirrors the pattern in perennia-reference-app.
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    # perennia-auth
    auth_signing_secret: str
    require_email_verification: bool

    # perennia-files
    files_signing_secret: str
    files_storage_path: str
    files_max_upload_size: int

    # sentinel-auth (RBAC service, replaces perennia-access)
    sentinel_service_url: str
    sentinel_client_key: str

    # Application
    cors_origins: list
    environment: str
    default_admin_email: str
    default_admin_password: str

    # AI Factory Assistant (DeepSeek). Optional - the assistant degrades to a
    # "not configured" reply rather than failing startup when unset.
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str


def load_settings() -> Settings:
    signing_secret = os.getenv("AUTH_SIGNING_SECRET", "")
    if not signing_secret:
        raise RuntimeError(
            "AUTH_SIGNING_SECRET is not set. Copy .env.example to .env and set a long, "
            "random value before starting the application."
        )

    files_secret = os.getenv("FILES_SIGNING_SECRET", "")
    if not files_secret:
        raise RuntimeError(
            "FILES_SIGNING_SECRET is not set. Copy .env.example to .env and set a long, "
            "random value before starting the application."
        )

    cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    sentinel_client_key = os.getenv("SENTINEL_CLIENT_KEY", "").strip()
    if not sentinel_client_key:
        raise RuntimeError(
            "SENTINEL_CLIENT_KEY is not set. This must be the UUID4 client key "
            "issued for JDK's tenant in the sentinel-auth service."
        )
    try:
        if str(uuid.UUID(sentinel_client_key, version=4)) != sentinel_client_key.lower():
            raise ValueError
    except ValueError:
        raise RuntimeError(
            f"SENTINEL_CLIENT_KEY={sentinel_client_key!r} is not a valid UUID4. "
            "Check for stray whitespace/quotes in .env, and that it matches the "
            "SENTINEL_CLIENT_KEY in sentinel-auth's own .env exactly."
        )

    return Settings(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "3306")),
        db_user=os.getenv("DB_USER", "root"),
        db_password=os.getenv("DB_PASSWORD", ""),
        db_name=os.getenv("DB_NAME", "jdk"),
        auth_signing_secret=signing_secret,
        require_email_verification=_get_bool("REQUIRE_EMAIL_VERIFICATION", False),
        files_signing_secret=files_secret,
        files_storage_path=os.getenv("FILES_STORAGE_PATH", "./var/files"),
        files_max_upload_size=int(os.getenv("FILES_MAX_UPLOAD_SIZE", str(50 * 1024 * 1024))),
        cors_origins=[o.strip() for o in cors_origins_raw.split(",") if o.strip()],
        environment=os.getenv("ENVIRONMENT", "development"),
        default_admin_email=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@jdk.local"),
        default_admin_password=os.getenv("DEFAULT_ADMIN_PASSWORD", ""),
        sentinel_service_url=os.getenv("SENTINEL_SERVICE_URL", "http://localhost:4000"),
        sentinel_client_key=sentinel_client_key,
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", "").strip(),
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    )
