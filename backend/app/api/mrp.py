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
from app.permissions.definitions import MRP_VIEW, MRP_EXECUTE
from app.models.mrp import MrpSnapshot, AtpResult

router = APIRouter(prefix="/api/mrp", tags=["mrp"])

_db = Database(load_settings())
_engine = MrpEngine(
    OrderRepository(_db), ProductRepository(_db), InventoryRepository(_db), SupplierRepository(_db),
)


@router.get("", response_model=MrpSnapshot)
def calculate_mrp(identity: AuthenticatedIdentity = Depends(require_permission(MRP_EXECUTE))):
    return MrpSnapshot(**_engine.calculate())


@router.get("/materials/{material_id}/why-required")
def why_material_required(material_id: int, identity: AuthenticatedIdentity = Depends(require_permission(MRP_VIEW))):
    return _engine.why_is_material_required(material_id)


@router.get("/atp", response_model=AtpResult)
def available_to_promise(product_id: int, requested_kg: float,
                          identity: AuthenticatedIdentity = Depends(require_permission(MRP_VIEW))):
    return AtpResult(**_engine.available_to_promise(product_id, requested_kg))
