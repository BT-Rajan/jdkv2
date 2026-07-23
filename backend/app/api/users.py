from fastapi import APIRouter, Depends, Query

from perennia_access import AuthenticatedIdentity

from app.core.security import auth, access, notify, require_permission
from app.core.database import Database
from app.core.config import load_settings
from app.domain.users.repository import UserAdminRepository
from app.domain.users.service import UserAdminService
from app.permissions.definitions import USERS_VIEW, USERS_MANAGE
from app.models.users import (
    CreateUserRequest, UpdateUserProfileRequest, ChangeRoleRequest,
    UserListResponse, UserSummary, AuditEntry,
)

router = APIRouter(prefix="/api/users", tags=["users"])

_settings = load_settings()
_db = Database(_settings)
_service = UserAdminService(auth, access, notify, UserAdminRepository(_db))


@router.get("", response_model=UserListResponse)
def search_users(
    q: str | None = Query(None),
    status: str | None = Query(None),
    role: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(USERS_VIEW)),
):
    rows, total = _service.search(q, status, role, limit, offset)
    return UserListResponse(
        users=[UserSummary(**row) for row in rows],
        total=total,
    )


@router.get("/{subject_id}", response_model=UserSummary)
def get_user(subject_id: str, identity: AuthenticatedIdentity = Depends(require_permission(USERS_VIEW))):
    return UserSummary(**_service.get(subject_id))


@router.get("/{subject_id}/audit", response_model=list[AuditEntry])
def get_user_audit(subject_id: str, identity: AuthenticatedIdentity = Depends(require_permission(USERS_VIEW))):
    return [AuditEntry(**row) for row in _service.audit_trail(subject_id)]


@router.post("", response_model=UserSummary)
def create_user(body: CreateUserRequest, identity: AuthenticatedIdentity = Depends(require_permission(USERS_MANAGE))):
    result = _service.create_user(
        identity, body.email, body.initial_password, body.full_name,
        body.phone, body.department, body.role,
    )
    return UserSummary(**result)


@router.patch("/{subject_id}/profile", response_model=UserSummary)
def update_profile(subject_id: str, body: UpdateUserProfileRequest,
                    identity: AuthenticatedIdentity = Depends(require_permission(USERS_MANAGE))):
    result = _service.update_profile(identity, subject_id, body.full_name, body.phone, body.department)
    return UserSummary(**result)


@router.post("/{subject_id}/role", response_model=UserSummary)
def change_role(subject_id: str, body: ChangeRoleRequest,
                 identity: AuthenticatedIdentity = Depends(require_permission(USERS_MANAGE))):
    result = _service.change_role(identity, subject_id, body.role)
    return UserSummary(**result)


@router.post("/{subject_id}/deactivate", response_model=UserSummary)
def deactivate_user(subject_id: str, identity: AuthenticatedIdentity = Depends(require_permission(USERS_MANAGE))):
    result = _service.deactivate(identity, subject_id)
    return UserSummary(**result)
