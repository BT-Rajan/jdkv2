"""
Integration seam.

Every protected route depends on `get_current_identity` (perennia-auth) and,
where authorization matters, `require_permission(...)` (perennia-access).
No route implements its own token parsing or its own role checks - this is
the one place those concerns live, mirroring perennia-reference-app's
`app/deps.py`.

This module also constructs the perennia-search, perennia-notify and
perennia-files clients, each wired with the same PerenniaAccess instance so
every package enforces JDK's own permission vocabulary (see
app/permissions/definitions.py) rather than JDK re-implementing checks.
"""
from fastapi import Depends, Header

from perennia_auth import PerenniaAuth, AuthConfig, DatabaseConfig as AuthDatabaseConfig
from perennia_access import (
    PerenniaAccess,
    AccessConfig,
    DatabaseConfig as AccessDatabaseConfig,
    AuthenticatedIdentity,
)
from perennia_search import PerenniaSearch, SearchConfig, DatabaseConfig as SearchDatabaseConfig
from perennia_notify import PerenniaNotify, NotifyConfig, DatabaseConfig as NotifyDatabaseConfig
from perennia_files import PerenniaFiles, FilesConfig, DatabaseConfig as FilesDatabaseConfig

from app.core.config import load_settings
from app.core.errors import AppError
from app.core.mailer import ConsoleMailer
from app.core.notify_channels import ConsoleEmailChannel

settings = load_settings()

# --- perennia-auth: who is this user? ---------------------------------------
auth = PerenniaAuth(
    AuthConfig(
        signing_secret=settings.auth_signing_secret,
        database=AuthDatabaseConfig(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
        ),
        require_email_verification=settings.require_email_verification,
    ),
    mailer=ConsoleMailer(frontend_base_url="http://localhost:5173"),
)

# --- perennia-access: what may this user do? --------------------------------
access = PerenniaAccess(
    AccessConfig(
        database=AccessDatabaseConfig(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
        ),
    )
)

# --- perennia-search: keyword search across JDK's business resources -------
search = PerenniaSearch(
    SearchConfig(
        database=SearchDatabaseConfig(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
        ),
    ),
    access=access,
)

# --- perennia-notify: notification infrastructure ---------------------------
notify = PerenniaNotify(
    NotifyConfig(
        database=NotifyDatabaseConfig(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
        ),
    ),
    access=access,
)
notify.register_channel("email", ConsoleEmailChannel())

# --- perennia-files: secure file storage ------------------------------------
files = PerenniaFiles(
    FilesConfig(
        storage_path=settings.files_storage_path,
        signing_secret=settings.files_signing_secret,
        database=FilesDatabaseConfig(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
        ),
        max_upload_size=settings.files_max_upload_size,
    ),
    access=access,
)


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppError("authentication_required")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise AppError("authentication_required")
    return token


def get_current_identity(
    authorization: str | None = Header(default=None),
) -> AuthenticatedIdentity:
    """Authenticate the request via perennia-auth and return the
    AuthenticatedIdentity contract perennia-access (and, by extension,
    perennia-search / perennia-notify / perennia-files) expect.
    """
    token = _extract_bearer_token(authorization)
    claims = auth.verify_access_token(token)
    return AuthenticatedIdentity(subject_id=claims["sub"], session_id=claims["sid"])


def require_permission(permission_code: str):
    """Dependency factory: require a specific permission via perennia-access.

    Usage: `identity = Depends(require_permission("customer.view"))`
    """

    def _dependency(
        identity: AuthenticatedIdentity = Depends(get_current_identity),
    ) -> AuthenticatedIdentity:
        access.require(identity, permission_code)
        return identity

    return _dependency
