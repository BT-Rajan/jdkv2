from fastapi import APIRouter, Depends

from perennia_access import AuthenticatedIdentity

from app.core.security import auth, access, get_current_identity
from app.models.users import LoginRequest, TokenResponse, RefreshRequest, MeResponse
from app.domain.users.service import UserAdminService
from app.domain.users.repository import UserAdminRepository
from app.core.database import Database
from app.core.config import load_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

_settings = load_settings()
_db = Database(_settings)
_repo = UserAdminRepository(_db)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    result = auth.authenticate(body.email, body.password)
    return TokenResponse(
        access_token=result.access_token,
        access_token_expires_at=result.access_token_expires_at,
        refresh_token=result.refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest):
    result = auth.refresh(body.refresh_token)
    return TokenResponse(
        access_token=result.access_token,
        access_token_expires_at=result.access_token_expires_at,
        refresh_token=result.refresh_token,
    )


@router.post("/logout")
def logout(identity: AuthenticatedIdentity = Depends(get_current_identity)):
    auth.logout(identity.session_id)
    return {"status": "logged_out"}


@router.post("/verify-email")
def verify_email(token: str):
    auth.verify_email(token)
    return {"status": "verified"}


@router.post("/forgot-password")
def forgot_password(email: str):
    auth.request_password_recovery(email)
    # Deliberately always 200: perennia-auth never reveals whether the
    # account exists, and neither does JDK.
    return {"status": "if_account_exists_email_sent"}


@router.post("/reset-password")
def reset_password(token: str, new_password: str):
    auth.reset_password(token, new_password)
    return {"status": "password_reset"}


@router.get("/me", response_model=MeResponse)
def me(identity: AuthenticatedIdentity = Depends(get_current_identity)):
    identifier = _repo.get_identifier(identity.subject_id)
    profile = _repo.get_profile(identity.subject_id) or {}
    roles = access.get_identity_roles(identity)
    permissions = access.get_identity_permissions(identity)
    return MeResponse(
        subject_id=identity.subject_id,
        email=identifier["email"] if identifier else None,
        full_name=profile.get("full_name"),
        department=profile.get("department"),
        roles=roles,
        permissions=permissions,
    )
