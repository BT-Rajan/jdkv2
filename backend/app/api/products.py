from fastapi import APIRouter, Depends, Query

from perennia_access import AuthenticatedIdentity

from app.core.security import require_permission, search as search_client
from app.core.database import Database
from app.core.config import load_settings
from app.domain.products.repository import ProductRepository
from app.domain.products.service import ProductService
from app.permissions.definitions import PRODUCTS_VIEW, PRODUCTS_MANAGE
from app.models.products import (
    ProductCreateRequest, ProductUpdateRequest, ProductStatusRequest,
    FormulaVersionRequest, FinishedGoodsMovementRequest,
    ProductResponse, ProductListResponse,
)

router = APIRouter(prefix="/api/products", tags=["products"])

_db = Database(load_settings())
_service = ProductService(ProductRepository(_db), search_client)


@router.get("", response_model=ProductListResponse)
def search_products(
    q: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(PRODUCTS_VIEW)),
):
    rows, total = _service.search(q, status, limit, offset)
    return ProductListResponse(products=[ProductResponse(**r) for r in rows], total=total)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, identity: AuthenticatedIdentity = Depends(require_permission(PRODUCTS_VIEW))):
    return ProductResponse(**_service.get(product_id))


@router.post("", response_model=ProductResponse)
def create_product(body: ProductCreateRequest, identity: AuthenticatedIdentity = Depends(require_permission(PRODUCTS_MANAGE))):
    return ProductResponse(**_service.create(
        identity, body.name, body.category, body.unit_of_measure, body.default_bag_size_kg,
    ))


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, body: ProductUpdateRequest,
                    identity: AuthenticatedIdentity = Depends(require_permission(PRODUCTS_MANAGE))):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    return ProductResponse(**_service.update(identity, product_id, data))


@router.post("/{product_id}/status", response_model=ProductResponse)
def set_product_status(product_id: int, body: ProductStatusRequest,
                        identity: AuthenticatedIdentity = Depends(require_permission(PRODUCTS_MANAGE))):
    return ProductResponse(**_service.set_status(identity, product_id, body.status))


@router.post("/{product_id}/formula-versions", response_model=ProductResponse)
def create_formula_version(product_id: int, body: FormulaVersionRequest,
                            identity: AuthenticatedIdentity = Depends(require_permission(PRODUCTS_MANAGE))):
    return ProductResponse(**_service.create_formula_version(
        identity, product_id, body.effective_from,
        [line.model_dump() for line in body.lines],
    ))


@router.post("/{product_id}/finished-goods/movements", response_model=dict)
def record_finished_goods_movement(product_id: int, body: FinishedGoodsMovementRequest,
                                    identity: AuthenticatedIdentity = Depends(require_permission(PRODUCTS_MANAGE))):
    return _service.record_finished_goods_movement(identity, product_id, body.delta_kg)
