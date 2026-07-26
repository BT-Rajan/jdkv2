from fastapi import APIRouter, Depends, Query

from app.core.sentinel_access import AuthenticatedIdentity
from app.core.security import require_permission
from app.core.database import Database
from app.core.config import load_settings
from app.domain.feasibility.repository import FeasibilityRepository
from app.domain.feasibility.service import FeasibilityService
from app.domain.customers.repository import CustomerRepository
from app.domain.products.repository import ProductRepository
from app.domain.orders.repository import OrderRepository
from app.domain.suppliers.repository import SupplierRepository
from app.domain.inventory.repository import InventoryRepository
from app.intelligence.mrp_engine import MrpEngine
from app.intelligence.feasibility_engine import FeasibilityEngine
from app.permissions.definitions import FEASIBILITY_VIEW, FEASIBILITY_RUN, HISTORY_AMEND
from app.models.feasibility import (
    FeasibilityRunRequest, FeasibilityRunResponse, FeasibilityListResponse, FeasibilityAmendRequest,
)

router = APIRouter(prefix="/api/feasibility", tags=["feasibility-workflow"])

_db = Database(load_settings())
_repo = FeasibilityRepository(_db)
_order_repo = OrderRepository(_db)
_inventory_repo = InventoryRepository(_db)
_mrp_engine = MrpEngine(_order_repo, ProductRepository(_db), _inventory_repo, SupplierRepository(_db))
_engine = FeasibilityEngine(_order_repo, _mrp_engine)
_service = FeasibilityService(_repo, CustomerRepository(_db), ProductRepository(_db), _engine)


@router.get("", response_model=FeasibilityListResponse)
def search_runs(
    customer_id: int | None = Query(None),
    outcome: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(FEASIBILITY_VIEW)),
):
    rows, total = _service.search(customer_id, outcome, status, limit, offset)
    return FeasibilityListResponse(runs=[FeasibilityRunResponse(**r) for r in rows], total=total)


@router.get("/{run_id}", response_model=FeasibilityRunResponse)
def get_run(run_id: str, identity: AuthenticatedIdentity = Depends(require_permission(FEASIBILITY_VIEW))):
    return FeasibilityRunResponse(**_service.get(run_id))


@router.post("", response_model=FeasibilityRunResponse)
def run_feasibility(body: FeasibilityRunRequest,
                     identity: AuthenticatedIdentity = Depends(require_permission(FEASIBILITY_RUN))):
    return FeasibilityRunResponse(**_service.run(
        identity, body.customer_id, body.product_id, body.quantity_kg,
        body.requested_delivery_date, body.notes,
    ))


@router.patch("/{run_id}", response_model=FeasibilityRunResponse)
def amend_run(run_id: str, body: FeasibilityAmendRequest,
              identity: AuthenticatedIdentity = Depends(require_permission(HISTORY_AMEND))):
    """Administrator-only. Feasibility history is otherwise immutable and
    never deletable - see docs/features/feasibility-and-risk.md."""
    return FeasibilityRunResponse(**_service.amend(identity, run_id, body.notes))
