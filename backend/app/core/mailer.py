"""
Mailer implementation for perennia-auth.

perennia-auth requires the consuming application to supply a Mailer
(see perennia_auth.mailer.Mailer). JDK does not ship an SMTP integration in
this codebase - that is a deployment concern - so this prints links to the
backend console instead. Swap this for a real Mailer implementation
(SMTP, SES, SendGrid, ...) before production use; nothing else in the
authentication flow needs to change.
"""
from urllib.parse import urlencode


class ConsoleMailer:
    def __init__(self, frontend_base_url: str):
        self._frontend_base_url = frontend_base_url.rstrip("/")

    def _print(self, heading: str, link: str) -> None:
        print("\n" + "=" * 72)
        print(f"[ConsoleMailer] {heading}")
        print(link)
        print("=" * 72 + "\n")

    def send_verification_email(self, email: str, raw_token: str) -> None:
        link = f"{self._frontend_base_url}/verify-email?{urlencode({'token': raw_token})}"
        self._print(f"Verify email for {email}", link)

    def send_email_change_verification(self, new_email: str, raw_token: str) -> None:
        link = f"{self._frontend_base_url}/verify-email?{urlencode({'token': raw_token})}"
        self._print(f"Confirm new email {new_email}", link)

    def send_password_recovery_email(self, email: str, raw_token: str) -> None:
        link = f"{self._frontend_base_url}/reset-password?{urlencode({'token': raw_token})}"
        self._print(f"Reset password for {email}", link)

    def notify_email_changed(self, old_email: str, new_email: str) -> None:
        self._print("Email address changed", f"{old_email} -> {new_email}")
