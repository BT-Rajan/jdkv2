from fastapi import APIRouter, Depends

from app.core.sentinel_access import AuthenticatedIdentity
from app.core.security import require_permission
from app.core.database import Database
from app.core.config import load_settings as load_app_config
from app.domain.settings.repository import SettingsRepository
from app.domain.settings.service import SettingsService
from app.permissions.definitions import SETTINGS_VIEW, SETTINGS_MANAGE
from app.models.settings import AppSettings, UpdateSettingsRequest

router = APIRouter(prefix="/api/settings", tags=["settings"])

_app_config = load_app_config()
_db = Database(_app_config)
_service = SettingsService(SettingsRepository(_db))


@router.get("", response_model=AppSettings)
def get_settings(identity: AuthenticatedIdentity = Depends(require_permission(SETTINGS_VIEW))):
    return _service.get()


@router.patch("", response_model=AppSettings)
def update_settings(
    body: UpdateSettingsRequest,
    identity: AuthenticatedIdentity = Depends(require_permission(SETTINGS_MANAGE)),
):
    return _service.update(body)
