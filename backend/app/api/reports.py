from fastapi import APIRouter, Depends

from perennia_access import AuthenticatedIdentity

from app.core.security import require_permission
from app.core.database import Database
from app.core.config import load_settings
from app.domain.orders.repository import OrderRepository
from app.domain.products.repository import ProductRepository
from app.domain.inventory.repository import InventoryRepository
from app.domain.suppliers.repository import SupplierRepository
from app.intelligence.mrp_engine import MrpEngine
from app.intelligence.feasibility_engine import FeasibilityEngine
from app.intelligence.dashboard import DashboardService
from app.permissions.definitions import MRP_VIEW, REPORTS_VIEW

router = APIRouter(prefix="/api", tags=["feasibility", "reports"])

_db = Database(load_settings())
_order_repo = OrderRepository(_db)
_inventory_repo = InventoryRepository(_db)
_mrp_engine = MrpEngine(_order_repo, ProductRepository(_db), _inventory_repo, SupplierRepository(_db))
_feasibility_engine = FeasibilityEngine(_order_repo, _mrp_engine)
_dashboard = DashboardService(_order_repo, _inventory_repo, _mrp_engine, _feasibility_engine)


@router.get("/orders/{order_id}/feasibility")
def assess_order_feasibility(order_id: int, identity: AuthenticatedIdentity = Depends(require_permission(MRP_VIEW))):
    return _feasibility_engine.assess_order(order_id)


@router.get("/feasibility/open-orders")
def assess_all_open_orders(identity: AuthenticatedIdentity = Depends(require_permission(MRP_VIEW))):
    return _feasibility_engine.assess_all_open_orders()


@router.get("/dashboard")
def dashboard(identity: AuthenticatedIdentity = Depends(require_permission(REPORTS_VIEW))):
    return _dashboard.summary()
