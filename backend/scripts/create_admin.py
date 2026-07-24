"""
Create the first login-ready Administrator account.

perennia-auth requires every new account to verify its own email before it
can authenticate - JDK does not bypass that (see app/core/mailer.py). For
the very first administrator, there is no other admin yet to send an
invite, so this script captures perennia-auth's own verification token
in-process (standing in for clicking the email link) instead of reusing the
real console/production mailer. This is the same technique
perennia-reference-app's seed_demo_data.py uses for its demo accounts.

Usage (from backend/, with the virtualenv active and .env configured):

    python scripts/create_admin.py you@company.com "a-strong-password" "Your Name"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from perennia_auth import PerenniaAuth, AuthConfig, DatabaseConfig as AuthDatabaseConfig, EmailAlreadyExistsError
from perennia_access import PerenniaAccess, AccessConfig, DatabaseConfig as AccessDatabaseConfig

from app.core.config import load_settings
from app.core.database import Database
from app.domain.users.repository import UserAdminRepository
from app.permissions import definitions as permission_definitions


class CapturingMailer:
    def __init__(self):
        self.last_verification_token = None

    def send_verification_email(self, email, raw_token):
        self.last_verification_token = raw_token

    def send_email_change_verification(self, new_email, raw_token):
        pass

    def send_password_recovery_email(self, email, raw_token):
        pass

    def notify_email_changed(self, old_email, new_email):
        pass


def run(email: str, password: str, full_name: str):
    """Create the admin and return its subject_id, or None if it already existed."""
    settings = load_settings()
    mailer = CapturingMailer()

    auth = PerenniaAuth(
        AuthConfig(
            signing_secret=settings.auth_signing_secret,
            database=AuthDatabaseConfig(
                host=settings.db_host, port=settings.db_port, user=settings.db_user,
                password=settings.db_password, database=settings.db_name,
            ),
            require_email_verification=settings.require_email_verification,
        ),
        mailer=mailer,
    )
    access = PerenniaAccess(
        AccessConfig(
            database=AccessDatabaseConfig(
                host=settings.db_host, port=settings.db_port, user=settings.db_user,
                password=settings.db_password, database=settings.db_name,
            )
        )
    )
    permission_definitions.seed(access)

    try:
        subject_id = auth.register(email, password)
    except EmailAlreadyExistsError:
        print(f"{email} already exists - not creating a duplicate.")
        return None

    auth.verify_email(mailer.last_verification_token)
    access.assign_role_to_user(subject_id, "administrator")

    repo = UserAdminRepository(Database(settings))
    repo.upsert_profile(subject_id, full_name, None, None)

    print(f"Administrator created: {email} (subject_id={subject_id})")
    return subject_id


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python scripts/create_admin.py <email> <password> <full name>")
        sys.exit(1)

    email, password, full_name = sys.argv[1], sys.argv[2], sys.argv[3]
    run(email, password, full_name)


if __name__ == "__main__":
    main()
