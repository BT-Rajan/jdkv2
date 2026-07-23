"""
Application settings.

All configuration is read from environment variables (see .env.example at
the repository root). Nothing here is hardcoded secret data - only
structural defaults for local development.
"""
from dataclasses import dataclass
import os
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

    # Application
    cors_origins: list
    environment: str
    default_admin_email: str
    default_admin_password: str


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
    )
