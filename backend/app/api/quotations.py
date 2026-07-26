from datetime import date

from fastapi import APIRouter, Depends, Query

from app.core.sentinel_access import AuthenticatedIdentity
from app.core.security import require_permission, search as search_client, notify as notify_client
from app.core.database import Database
from app.core.config import load_settings
from app.core.errors import AppError
from app.domain.quotations.repository import QuotationRepository
from app.domain.quotations.service import QuotationService
from app.domain.feasibility.repository import FeasibilityRepository
from app.domain.orders.repository import OrderRepository
from app.domain.orders.service import OrderService
from app.domain.products.repository import ProductRepository
from app.domain.customers.repository import CustomerRepository
from app.permissions.definitions import SALES_ACCESS, HISTORY_AMEND
from app.models.quotations import (
    QuotationCreateRequest, QuotationUpdateRequest, QuotationStatusRequest,
    QuotationResponse, QuotationListResponse, ConvertToOrderRequest,
)
from app.models.orders import OrderResponse

router = APIRouter(prefix="/api/quotations", tags=["quotations"])

_db = Database(load_settings())
_repo = QuotationRepository(_db)
_feasibility_repo = FeasibilityRepository(_db)
_order_repo = OrderRepository(_db)
_service = QuotationService(_repo, _feasibility_repo, _order_repo)
_order_service = OrderService(_order_repo, ProductRepository(_db), CustomerRepository(_db), search_client, notify_client)


@router.get("", response_model=QuotationListResponse)
def search_quotations(
    customer_id: int | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(SALES_ACCESS)),
):
    rows, total = _service.search(customer_id, status, limit, offset)
    return QuotationListResponse(quotations=[QuotationResponse(**r) for r in rows], total=total)


@router.get("/{quote_id}", response_model=QuotationResponse)
def get_quotation(quote_id: str, identity: AuthenticatedIdentity = Depends(require_permission(SALES_ACCESS))):
    return QuotationResponse(**_service.get(quote_id))


@router.post("", response_model=QuotationResponse)
def create_quotation(body: QuotationCreateRequest,
                      identity: AuthenticatedIdentity = Depends(require_permission(SALES_ACCESS))):
    """Only available when the linked feasibility check passed - see
    FeasibilityService/OUTCOMES_ALLOWING_QUOTATION - this is the
    'Generate quotation' button in the feasibility workflow."""
    return QuotationResponse(**_service.create(
        identity, body.feasibility_id, body.unit_price, body.valid_until, body.terms, body.notes,
    ))


@router.patch("/{quote_id}", response_model=QuotationResponse)
def update_quotation(quote_id: str, body: QuotationUpdateRequest,
                      identity: AuthenticatedIdentity = Depends(require_permission(SALES_ACCESS))):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    return QuotationResponse(**_service.update(identity, quote_id, data))


@router.post("/{quote_id}/status", response_model=QuotationResponse)
def set_status(quote_id: str, body: QuotationStatusRequest,
                identity: AuthenticatedIdentity = Depends(require_permission(SALES_ACCESS))):
    return QuotationResponse(**_service.set_status(identity, quote_id, body.status))


@router.patch("/{quote_id}/amend", response_model=QuotationResponse)
def amend_quotation(quote_id: str, body: QuotationUpdateRequest,
                     identity: AuthenticatedIdentity = Depends(require_permission(HISTORY_AMEND))):
    """Administrator-only correction of a finalized (non-draft) quotation."""
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    return QuotationResponse(**_service.amend(identity, quote_id, data))


@router.post("/{quote_id}/convert-to-order", response_model=OrderResponse)
def convert_to_order(quote_id: str, body: ConvertToOrderRequest,
                      identity: AuthenticatedIdentity = Depends(require_permission(SALES_ACCESS))):
    """Only an accepted quotation can become an order (workflow:
    feasibility -> quotation -> order -> delivery). customer, product and
    quantity are copied from the quotation and are never accepted from the
    request body."""
    quotation = _service.get(quote_id)
    if quotation["status"] != "accepted":
        raise AppError("conflict")

    order_date = body.order_date or date.today()
    order = _order_service.create_from_quotation(
        identity, quotation, order_date, body.delivery_date,
        body.bag_size_kg, body.priority, body.notes,
    )
    _service.mark_converted(quote_id)
    return OrderResponse(**order)
