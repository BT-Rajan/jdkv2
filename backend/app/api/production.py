from fastapi import APIRouter, Depends

from app.core.sentinel_access import AuthenticatedIdentity
from app.core.security import require_permission
from app.core.database import Database
from app.core.config import load_settings
from app.domain.production.repository import ProductionCycleRepository
from app.domain.production.service import ProductionCycleService
from app.domain.products.repository import ProductRepository
from app.permissions.definitions import PRODUCTS_VIEW, PRODUCTS_MANAGE
from app.models.production import ProductionCycleUpsertRequest, ProductionCycleResponse

router = APIRouter(prefix="/api/products/{product_id}/production-cycle", tags=["production"])

_db = Database(load_settings())
_service = ProductionCycleService(ProductionCycleRepository(_db), ProductRepository(_db))


@router.get("", response_model=ProductionCycleResponse)
def get_production_cycle(
    product_id: int,
    identity: AuthenticatedIdentity = Depends(require_permission(PRODUCTS_VIEW)),
):
    return ProductionCycleResponse(**_service.get(product_id))


@router.put("", response_model=ProductionCycleResponse)
def upsert_production_cycle(
    product_id: int,
    body: ProductionCycleUpsertRequest,
    identity: AuthenticatedIdentity = Depends(require_permission(PRODUCTS_MANAGE)),
):
    return ProductionCycleResponse(**_service.upsert(product_id, body.model_dump()))
