from fastapi import APIRouter, Depends, Query

from app.core.sentinel_access import AuthenticatedIdentity
from app.core.security import require_permission
from app.core.database import Database
from app.core.config import load_settings
from app.domain.deliveries.repository import DeliveryRepository
from app.domain.deliveries.service import DeliveryService
from app.domain.orders.repository import OrderRepository
from app.permissions.definitions import DELIVERIES_VIEW, DELIVERIES_MANAGE, HISTORY_AMEND
from app.models.deliveries import (
    DeliveryCreateRequest, DeliveryStatusRequest, DeliveryResponse, DeliveryListResponse,
)

router = APIRouter(prefix="/api/deliveries", tags=["deliveries"])

_db = Database(load_settings())
_order_repo = OrderRepository(_db)
_repo = DeliveryRepository(_db)
_service = DeliveryService(_repo, _order_repo)


@router.get("", response_model=DeliveryListResponse)
def search_deliveries(
    order_id: int | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(DELIVERIES_VIEW)),
):
    rows, total = _service.search(order_id, status, limit, offset)
    return DeliveryListResponse(deliveries=[DeliveryResponse(**r) for r in rows], total=total)


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: str, identity: AuthenticatedIdentity = Depends(require_permission(DELIVERIES_VIEW))):
    return DeliveryResponse(**_service.get(delivery_id))


@router.post("", response_model=DeliveryResponse)
def create_delivery(body: DeliveryCreateRequest,
                     identity: AuthenticatedIdentity = Depends(require_permission(DELIVERIES_MANAGE))):
    """Only issuable against an existing order - see docs/features: delivery
    is the last stage of feasibility -> quotation -> order -> delivery."""
    return DeliveryResponse(**_service.create(
        identity, body.order_id, body.delivery_date, body.dispatched_qty_kg,
        body.carrier, body.tracking_ref, body.notes,
    ))


@router.post("/{delivery_id}/status", response_model=DeliveryResponse)
def set_status(delivery_id: str, body: DeliveryStatusRequest,
                identity: AuthenticatedIdentity = Depends(require_permission(DELIVERIES_MANAGE))):
    return DeliveryResponse(**_service.set_status(identity, delivery_id, body.status))


@router.patch("/{delivery_id}/amend", response_model=DeliveryResponse)
def amend_delivery(delivery_id: str, body: DeliveryCreateRequest,
                    identity: AuthenticatedIdentity = Depends(require_permission(HISTORY_AMEND))):
    """Administrator-only correction of a finalized delivery record."""
    data = {k: v for k, v in body.model_dump().items() if v is not None and k != "order_id"}
    return DeliveryResponse(**_service.amend(identity, delivery_id, data))
