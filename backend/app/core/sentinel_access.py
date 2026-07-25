"""
SentinelAccess: replaces perennia_access.PerenniaAccess with a client for the
sentinel-auth RBAC service (BT-Rajan/perennia-auth, main branch).

Sentinel has no standalone "permission" entity - a permission only exists as
a grant on a role - and no role-existence lookup beyond listing all roles, so
get_permission/create_permission are approximated (see docstrings). Every
write endpoint on sentinel's side is an idempotent upsert, so repeated seed()
calls are safe.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

import requests


class AccessError(Exception):
    """exc.code is read by app.main's exception handler to resolve the HTTP
    status/message from app.core.errors.ACCESS_ERROR_CATALOG."""

    def __init__(self, code: str, message: Optional[str] = None):
        self.code = code
        super().__init__(message or code)


class RoleNotFoundError(AccessError):
    def __init__(self, role_code: str):
        super().__init__("role_not_found", f"Role '{role_code}' does not exist")
        self.role_code = role_code


@dataclass(frozen=True)
class AuthenticatedIdentity:
    subject_id: str
    session_id: Optional[str] = None


@dataclass(frozen=True)
class AccessConfig:
    service_url: str
    client_key: str
    timeout: int = 10


class SentinelAccess:
    def __init__(self, config: AccessConfig):
        self._base = config.service_url.rstrip("/")
        self._timeout = config.timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {config.client_key}",
            "Content-Type": "application/json",
        })

    def _request(self, method: str, path: str) -> Any:
        try:
            resp = self._session.request(method, f"{self._base}{path}", timeout=self._timeout)
        except requests.RequestException as e:
            raise AccessError("access_database_error", str(e)) from e
        if resp.status_code >= 500:
            raise AccessError("access_database_error", resp.text)
        if resp.status_code >= 400:
            raise AccessError("invalid_access_configuration", resp.text)
        try:
            return resp.json()
        except ValueError as e:
            raise AccessError("access_database_error", "Non-JSON response from sentinel") from e

    @staticmethod
    def _unwrap(payload: Any) -> Any:
        # sentinel wraps some endpoints as {"success":..,"data":..} and
        # others as bare {"result":..} - normalize both.
        if isinstance(payload, dict):
            if "data" in payload:
                return payload["data"]
            if "result" in payload:
                return payload["result"]
        return payload

    @staticmethod
    def _validate_identity(identity: AuthenticatedIdentity) -> None:
        if not identity or not identity.subject_id:
            raise AccessError("invalid_identity")

    # --- runtime checks, called on every request ----------------------------

    def can(self, identity: AuthenticatedIdentity, permission_code: str) -> bool:
        self._validate_identity(identity)
        data = self._unwrap(self._request("GET", f"/api/has_permission/{identity.subject_id}/{permission_code}"))
        if isinstance(data, dict):
            return bool(data.get("has_permission"))
        return bool(data)

    def require(self, identity: AuthenticatedIdentity, permission_code: str) -> None:
        if not self.can(identity, permission_code):
            raise AccessError("authorization_denied")

    def get_identity_permissions(self, identity: AuthenticatedIdentity) -> List[str]:
        self._validate_identity(identity)
        data = self._unwrap(self._request("GET", f"/api/user_permissions/{identity.subject_id}"))
        perms = data.get("permissions", []) if isinstance(data, dict) else (data or [])
        return [p["name"] for p in perms]

    def get_identity_roles(self, identity: AuthenticatedIdentity) -> List[str]:
        self._validate_identity(identity)
        data = self._unwrap(self._request("GET", f"/api/user_roles/{identity.subject_id}")) or []
        return [r["role"] for r in data]

    # --- seed/admin operations -----------------------------------------------

    def list_role_codes(self) -> List[str]:
        data = self._unwrap(self._request("GET", "/api/roles")) or []
        return [r["role"] for r in data]

    def get_role(self, code: str) -> Optional[str]:
        """No standalone role-existence endpoint on sentinel; approximated
        via the roles list so seed() can skip re-creating existing roles."""
        return code if code in self.list_role_codes() else None

    def create_role(self, code: str, description: str = "") -> None:
        self._request("POST", f"/api/role/{code}")

    def get_permission(self, code: str) -> None:
        """Sentinel has no standalone permission entity - always None so
        definitions.seed() calls create_permission (a no-op) every time and
        relies on assign_permission_to_role (idempotent) to do real work."""
        return None

    def create_permission(self, code: str, description: str = "") -> None:
        return None

    def get_role_permissions(self, role_code: str) -> List[str]:
        data = self._unwrap(self._request("GET", f"/api/role_permissions/{role_code}")) or []
        return [p["name"] for p in data]

    def assign_permission_to_role(self, role_code: str, permission_code: str) -> None:
        self._request("POST", f"/api/permission/{role_code}/{permission_code}")

    def assign_role_to_user(self, subject_id: str, role_code: str) -> None:
        if self.get_role(role_code) is None:
            raise RoleNotFoundError(role_code)
        self._request("POST", f"/api/membership/{subject_id}/{role_code}")

    def unassign_role_from_user(self, subject_id: str, role_code: str) -> bool:
        data = self._unwrap(self._request("DELETE", f"/api/membership/{subject_id}/{role_code}"))
        if isinstance(data, dict):
            return bool(data.get("result", True))
        return bool(data)
