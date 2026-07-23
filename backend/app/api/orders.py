from fastapi import APIRouter, Depends, Query

from perennia_access import AuthenticatedIdentity

from app.core.security import require_permission, search as search_client, notify as notify_client
from app.core.database import Database
from app.core.config import load_settings
from app.domain.orders.repository import OrderRepository
from app.domain.orders.service import OrderService
from app.domain.products.repository import ProductRepository
from app.domain.customers.repository import CustomerRepository
from app.permissions.definitions import ORDERS_VIEW, ORDERS_CREATE, ORDERS_EDIT, ORDERS_DELETE
from app.models.orders import (
    OrderCreateRequest, OrderUpdateRequest, OrderStatusRequest,
    OrderResponse, OrderListResponse, AvailabilityResponse,
)

router = APIRouter(prefix="/api/orders", tags=["orders"])

_db = Database(load_settings())
_service = OrderService(
    OrderRepository(_db), ProductRepository(_db), CustomerRepository(_db),
    search_client, notify_client,
)


@router.get("", response_model=OrderListResponse)
def search_orders(
    q: str | None = Query(None),
    status: str | None = Query(None),
    customer_id: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(ORDERS_VIEW)),
):
    rows, total = _service.search(q, status, customer_id, limit, offset)
    return OrderListResponse(orders=[OrderResponse(**r) for r in rows], total=total)


@router.get("/availability", response_model=AvailabilityResponse)
def check_availability(product_id: int, quantity_kg: float,
                        identity: AuthenticatedIdentity = Depends(require_permission(ORDERS_VIEW))):
    return AvailabilityResponse(**_service.check_availability(product_id, quantity_kg))


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, identity: AuthenticatedIdentity = Depends(require_permission(ORDERS_VIEW))):
    return OrderResponse(**_service.get(order_id))


@router.post("", response_model=OrderResponse)
def create_order(body: OrderCreateRequest, identity: AuthenticatedIdentity = Depends(require_permission(ORDERS_CREATE))):
    return OrderResponse(**_service.create(
        identity, body.customer_id, body.product_id, body.quantity_kg,
        body.bag_size_kg, body.delivery_date, body.priority, body.notes,
    ))


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, body: OrderUpdateRequest,
                  identity: AuthenticatedIdentity = Depends(require_permission(ORDERS_EDIT))):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    return OrderResponse(**_service.update(identity, order_id, data))


@router.post("/{order_id}/status", response_model=OrderResponse)
def set_order_status(order_id: int, body: OrderStatusRequest,
                      identity: AuthenticatedIdentity = Depends(require_permission(ORDERS_EDIT))):
    return OrderResponse(**_service.set_status(identity, order_id, body.status))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, identity: AuthenticatedIdentity = Depends(require_permission(ORDERS_DELETE))):
    return OrderResponse(**_service.set_status(identity, order_id, "cancelled"))
