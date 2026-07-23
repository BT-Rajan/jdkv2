from fastapi import APIRouter, Depends, Query

from perennia_access import AuthenticatedIdentity

from app.core.security import require_permission, search as search_client, notify as notify_client
from app.core.database import Database
from app.core.config import load_settings
from app.domain.inventory.repository import InventoryRepository
from app.domain.inventory.service import InventoryService
from app.domain.users.repository import UserAdminRepository
from app.permissions.definitions import INVENTORY_VIEW, INVENTORY_ADJUST
from app.models.inventory import (
    MaterialCreateRequest, ReorderConfigRequest, MovementRequest,
    MaterialResponse, MaterialListResponse,
)

router = APIRouter(prefix="/api/materials", tags=["inventory"])

_db = Database(load_settings())
_service = InventoryService(
    InventoryRepository(_db), search_client, notify_client, UserAdminRepository(_db),
)


@router.get("", response_model=MaterialListResponse)
def search_materials(
    q: str | None = Query(None),
    low_stock_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(INVENTORY_VIEW)),
):
    rows, total = _service.search(q, low_stock_only, limit, offset)
    return MaterialListResponse(materials=[MaterialResponse(**r) for r in rows], total=total)


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: int, identity: AuthenticatedIdentity = Depends(require_permission(INVENTORY_VIEW))):
    return MaterialResponse(**_service.get(material_id))


@router.post("", response_model=MaterialResponse)
def create_material(body: MaterialCreateRequest, identity: AuthenticatedIdentity = Depends(require_permission(INVENTORY_ADJUST))):
    return MaterialResponse(**_service.create_material(identity, body.name, body.unit))


@router.patch("/{material_id}/reorder-config", response_model=MaterialResponse)
def set_reorder_config(material_id: int, body: ReorderConfigRequest,
                        identity: AuthenticatedIdentity = Depends(require_permission(INVENTORY_ADJUST))):
    return MaterialResponse(**_service.set_reorder_config(
        identity, material_id, body.minimum_stock, body.reorder_point, body.lead_time_days,
    ))


@router.post("/{material_id}/movements", response_model=MaterialResponse)
def record_movement(material_id: int, body: MovementRequest,
                     identity: AuthenticatedIdentity = Depends(require_permission(INVENTORY_ADJUST))):
    return MaterialResponse(**_service.record_movement(
        identity, material_id, body.movement_type, body.quantity, body.reference,
    ))
