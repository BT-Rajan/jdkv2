from fastapi import APIRouter, Depends, Query

from perennia_access import AuthenticatedIdentity

from app.core.security import require_permission, search as search_client
from app.core.database import Database
from app.core.config import load_settings
from app.domain.customers.repository import CustomerRepository
from app.domain.customers.service import CustomerService
from app.permissions.definitions import CUSTOMERS_VIEW, CUSTOMERS_MANAGE
from app.models.customers import (
    CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse, CustomerListResponse,
)

router = APIRouter(prefix="/api/customers", tags=["customers"])

_db = Database(load_settings())
_service = CustomerService(CustomerRepository(_db), search_client)


@router.get("", response_model=CustomerListResponse)
def search_customers(
    q: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(CUSTOMERS_VIEW)),
):
    rows, total = _service.search(q, status, limit, offset)
    return CustomerListResponse(customers=[CustomerResponse(**r) for r in rows], total=total)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, identity: AuthenticatedIdentity = Depends(require_permission(CUSTOMERS_VIEW))):
    return CustomerResponse(**_service.get(customer_id))


@router.post("", response_model=CustomerResponse)
def create_customer(body: CustomerCreateRequest, identity: AuthenticatedIdentity = Depends(require_permission(CUSTOMERS_MANAGE))):
    return CustomerResponse(**_service.create(identity, body.model_dump()))


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, body: CustomerUpdateRequest,
                     identity: AuthenticatedIdentity = Depends(require_permission(CUSTOMERS_MANAGE))):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    return CustomerResponse(**_service.update(identity, customer_id, data))


@router.post("/{customer_id}/deactivate", response_model=CustomerResponse)
def deactivate_customer(customer_id: int, identity: AuthenticatedIdentity = Depends(require_permission(CUSTOMERS_MANAGE))):
    return CustomerResponse(**_service.deactivate(identity, customer_id))
