"""
Centralized error configuration.

Every error the API can return is declared here, once, as an
(http_status, public_message) pair keyed by a stable error code. No other
module hardcodes an HTTP status or a user-facing string - it raises an
AppError (below) or lets a perennia-auth / perennia-access / perennia-search
/ perennia-notify / perennia-files exception propagate, and the exception
handler in app.main looks the code up in this catalog.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorSpec:
    http_status: int
    message: str


# --- Application-level errors (raised directly by JDK's own code) ----------
APP_ERROR_CATALOG: dict[str, ErrorSpec] = {
    "authentication_required": ErrorSpec(401, "Please sign in to continue."),
    "invalid_or_expired_session": ErrorSpec(401, "Your session has expired. Please sign in again."),
    "validation_error": ErrorSpec(422, "Please check the information you entered."),
    "not_found": ErrorSpec(404, "The requested resource was not found."),
    "conflict": ErrorSpec(409, "This action conflicts with the current state of the record."),
    "http_error": ErrorSpec(400, "Request could not be processed."),
    "internal_error": ErrorSpec(500, "Something went wrong on our end. Please try again shortly."),
}

# --- perennia-auth errors ----------------------------------------------------
AUTH_ERROR_CATALOG: dict[str, ErrorSpec] = {
    "validation_error": ErrorSpec(422, "Please check the information you entered."),
    "weak_password": ErrorSpec(422, "Password does not meet the minimum strength requirements."),
    "invalid_email": ErrorSpec(422, "Please enter a valid email address."),
    "email_exists": ErrorSpec(409, "That email address could not be registered. It may already be in use."),
    "invalid_credentials": ErrorSpec(401, "Invalid email or password."),
    "account_not_authenticatable": ErrorSpec(403, "This account cannot sign in right now. Please verify your email or contact an administrator."),
    "account_locked": ErrorSpec(403, "This account is temporarily locked due to repeated failed sign-in attempts."),
    "invalid_token": ErrorSpec(400, "This link is invalid. Please request a new one."),
    "expired_token": ErrorSpec(400, "This link has expired. Please request a new one."),
    "token_already_used": ErrorSpec(400, "This link has already been used."),
    "too_many_attempts": ErrorSpec(429, "Too many attempts. Please wait a while before trying again."),
    "session_not_found": ErrorSpec(401, "Your session could not be found. Please sign in again."),
    "session_revoked": ErrorSpec(401, "Your session is no longer active. Please sign in again."),
    "auth_error": ErrorSpec(400, "We couldn't complete that request."),
}

# --- perennia-access errors --------------------------------------------------
ACCESS_ERROR_CATALOG: dict[str, ErrorSpec] = {
    "authorization_denied": ErrorSpec(403, "You do not have permission to do that."),
    "permission_not_found": ErrorSpec(500, "This area is not configured correctly. Please contact an administrator."),
    "role_not_found": ErrorSpec(500, "This area is not configured correctly. Please contact an administrator."),
    "invalid_access_configuration": ErrorSpec(500, "This area is not configured correctly. Please contact an administrator."),
    "access_database_error": ErrorSpec(503, "Authorization service is temporarily unavailable. Please try again shortly."),
    "invalid_identity": ErrorSpec(401, "Please sign in to continue."),
    "access_error": ErrorSpec(400, "We couldn't complete that request."),
}

FALLBACK = ErrorSpec(500, "Something went wrong on our end. Please try again shortly.")


def resolve(code: str) -> ErrorSpec:
    """Look up the (status, message) pair for an error code across all catalogs."""
    return (
        APP_ERROR_CATALOG.get(code)
        or AUTH_ERROR_CATALOG.get(code)
        or ACCESS_ERROR_CATALOG.get(code)
        or FALLBACK
    )


class AppError(Exception):
    """Raised by JDK's own code for application-level failures.

    `code` must be a key in APP_ERROR_CATALOG.
    """

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)
