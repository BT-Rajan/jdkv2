from datetime import datetime
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    access_token_expires_at: int
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class MeResponse(BaseModel):
    subject_id: str
    email: str | None
    full_name: str | None
    department: str | None
    roles: list[str]
    permissions: list[str]


class CreateUserRequest(BaseModel):
    email: EmailStr
    initial_password: str
    full_name: str
    phone: str | None = None
    department: str | None = None
    role: str


class UpdateUserProfileRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    department: str | None = None


class ChangeRoleRequest(BaseModel):
    role: str


class UserSummary(BaseModel):
    subject_id: str
    email: str
    full_name: str | None
    phone: str | None
    department: str | None
    status: str
    roles: list[str]
    created_at: datetime


class UserListResponse(BaseModel):
    users: list[UserSummary]
    total: int


class AuditEntry(BaseModel):
    actor_subject_id: str
    action: str
    target_subject_id: str
    previous_state: dict | None
    new_state: dict | None
    created_at: datetime
