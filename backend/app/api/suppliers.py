from fastapi import APIRouter, Depends, Query

from perennia_access import AuthenticatedIdentity

from app.core.security import require_permission, search as search_client
from app.core.database import Database
from app.core.config import load_settings
from app.domain.suppliers.repository import SupplierRepository
from app.domain.suppliers.service import SupplierService
from app.permissions.definitions import SUPPLIERS_VIEW, SUPPLIERS_MANAGE
from app.models.suppliers import (
    SupplierCreateRequest, SupplierUpdateRequest, SupplyTermsRequest,
    SupplierResponse, SupplierListResponse,
)

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])

_db = Database(load_settings())
_service = SupplierService(SupplierRepository(_db), search_client)


@router.get("", response_model=SupplierListResponse)
def search_suppliers(
    q: str | None = Query(None),
    category: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(SUPPLIERS_VIEW)),
):
    rows, total = _service.search(q, category, status, limit, offset)
    return SupplierListResponse(suppliers=[SupplierResponse(**r) for r in rows], total=total)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, identity: AuthenticatedIdentity = Depends(require_permission(SUPPLIERS_VIEW))):
    return SupplierResponse(**_service.get(supplier_id))


@router.post("", response_model=SupplierResponse)
def create_supplier(body: SupplierCreateRequest, identity: AuthenticatedIdentity = Depends(require_permission(SUPPLIERS_MANAGE))):
    return SupplierResponse(**_service.create(identity, body.model_dump()))


@router.patch("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, body: SupplierUpdateRequest,
                     identity: AuthenticatedIdentity = Depends(require_permission(SUPPLIERS_MANAGE))):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    return SupplierResponse(**_service.update(identity, supplier_id, data))


@router.post("/{supplier_id}/deactivate", response_model=SupplierResponse)
def deactivate_supplier(supplier_id: int, identity: AuthenticatedIdentity = Depends(require_permission(SUPPLIERS_MANAGE))):
    return SupplierResponse(**_service.deactivate(identity, supplier_id))


@router.put("/{supplier_id}/supply-terms", response_model=SupplierResponse)
def set_supply_terms(supplier_id: int, body: SupplyTermsRequest,
                      identity: AuthenticatedIdentity = Depends(require_permission(SUPPLIERS_MANAGE))):
    return SupplierResponse(**_service.set_supply_terms(
        identity, body.material_id, supplier_id, body.price, body.lead_time_days,
        body.minimum_order_qty, body.payment_terms, body.delivery_cost,
    ))
