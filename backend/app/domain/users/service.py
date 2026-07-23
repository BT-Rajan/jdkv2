"""
User administration domain service.

Implements docs/features/authentication-and-users.md: JDK provides the
admin-facing search/view/create/update/promote/demote/deactivate experience,
while identity stays owned by perennia-auth and roles/permissions stay owned
by perennia-access. This module is the only place those three are composed
for the user-management use case.
"""
from perennia_auth import PerenniaAuth, EmailAlreadyExistsError
from perennia_access import PerenniaAccess, AuthenticatedIdentity, RoleNotFoundError
from perennia_notify import PerenniaNotify

from app.core.errors import AppError
from app.domain.users.repository import UserAdminRepository
from app.permissions.definitions import SYSTEM_IDENTITY

ASSIGNABLE_ROLE_CODES = {"administrator", "executive", "operations", "production", "procurement"}


class UserAdminService:
    def __init__(self, auth: PerenniaAuth, access: PerenniaAccess,
                 notify: PerenniaNotify, repo: UserAdminRepository):
        self._auth = auth
        self._access = access
        self._notify = notify
        self._repo = repo

    # ------------------------------------------------------------- search/view

    def search(self, keyword: str | None, status: str | None, role: str | None,
               limit: int, offset: int) -> tuple[list[dict], int]:
        rows, total = self._repo.search(keyword, status, role, limit, offset)
        for row in rows:
            row["roles"] = self._access.get_identity_roles(
                AuthenticatedIdentity(subject_id=row["subject_id"], session_id="")
            )
        return rows, total

    def get(self, subject_id: str) -> dict:
        identifier = self._repo.get_identifier(subject_id)
        if not identifier:
            raise AppError("not_found")
        profile = self._repo.get_profile(subject_id) or {}
        roles = self._access.get_identity_roles(
            AuthenticatedIdentity(subject_id=subject_id, session_id="")
        )
        return {**identifier, **profile, "roles": roles}

    # ------------------------------------------------------------- mutations

    def create_user(self, actor: AuthenticatedIdentity, email: str, initial_password: str,
                     full_name: str, phone: str | None, department: str | None,
                     role: str) -> dict:
        if role not in ASSIGNABLE_ROLE_CODES:
            raise AppError("validation_error")

        try:
            subject_id = self._auth.register(email, initial_password)
        except EmailAlreadyExistsError:
            raise AppError("conflict")

        self._repo.upsert_profile(subject_id, full_name, phone, department)

        try:
            self._access.assign_role_to_user(subject_id, role)
        except RoleNotFoundError:
            raise AppError("validation_error")

        self._repo.record_audit(
            actor.subject_id, "user.created", subject_id,
            previous_state=None,
            new_state={"email": email, "role": role, "full_name": full_name},
        )

        # perennia-auth requires the new account to verify its own email
        # before it can authenticate (see ConsoleMailer note in
        # app/core/mailer.py) - JDK does not bypass that.
        return self.get(subject_id)

    def update_profile(self, actor: AuthenticatedIdentity, subject_id: str,
                        full_name: str | None, phone: str | None,
                        department: str | None) -> dict:
        before = self._repo.get_profile(subject_id) or {}
        merged = {
            "full_name": full_name if full_name is not None else before.get("full_name"),
            "phone": phone if phone is not None else before.get("phone"),
            "department": department if department is not None else before.get("department"),
        }
        self._repo.upsert_profile(subject_id, merged["full_name"], merged["phone"], merged["department"])
        self._repo.record_audit(actor.subject_id, "user.profile_updated", subject_id, before, merged)
        return self.get(subject_id)

    def change_role(self, actor: AuthenticatedIdentity, subject_id: str, new_role: str) -> dict:
        """Promote/demote: JDK maintains a single active role per user, so
        this unassigns every current role and assigns exactly the new one -
        a role change, not an additive grant. All of it is authorization
        state, so every step goes through perennia-access.
        """
        if new_role not in ASSIGNABLE_ROLE_CODES:
            raise AppError("validation_error")

        current_roles = self._access.get_identity_roles(
            AuthenticatedIdentity(subject_id=subject_id, session_id="")
        )
        for role_code in current_roles:
            self._access.unassign_role_from_user(subject_id, role_code)
        try:
            self._access.assign_role_to_user(subject_id, new_role)
        except RoleNotFoundError:
            raise AppError("validation_error")

        self._repo.record_audit(
            actor.subject_id, "user.role_changed", subject_id,
            previous_state={"roles": current_roles},
            new_state={"roles": [new_role]},
        )

        identifier = self._repo.get_identifier(subject_id)
        if identifier:
            self._notify.send(
                channel="email",
                recipient=identifier["email"],
                subject="Your JDK access level has changed",
                body=f"Your role changed from {', '.join(current_roles) or 'none'} to {new_role}.",
                subject_id=subject_id,
                identity=SYSTEM_IDENTITY,
            )

        return self.get(subject_id)

    def deactivate(self, actor: AuthenticatedIdentity, subject_id: str) -> dict:
        """Best-effort deactivation.

        perennia-auth does not expose a public "disable this subject" API
        (its own internal `locked` status is reserved for its brute-force
        policy, not an admin action) - and this application does not
        reimplement perennia-auth internals to add one. JDK's deactivation is
        therefore composed from the public surface both packages *do*
        expose: revoke every active session (perennia-auth) and strip every
        role assignment (perennia-access), so perennia-access denies every
        permission check for this user even though their credentials still
        technically exist. If perennia-auth later adds a real
        suspend/disable API, this should be swapped to use it directly.
        """
        current_roles = self._access.get_identity_roles(
            AuthenticatedIdentity(subject_id=subject_id, session_id="")
        )
        for role_code in current_roles:
            self._access.unassign_role_from_user(subject_id, role_code)
        self._auth.revoke_all_sessions(subject_id)

        self._repo.record_audit(
            actor.subject_id, "user.deactivated", subject_id,
            previous_state={"roles": current_roles},
            new_state={"roles": []},
        )
        return self.get(subject_id)

    def audit_trail(self, subject_id: str) -> list[dict]:
        return self._repo.list_audit_for_target(subject_id)
