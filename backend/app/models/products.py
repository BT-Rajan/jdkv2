from datetime import date, datetime
from pydantic import BaseModel


class ProductCreateRequest(BaseModel):
    name: str
    category: str | None = None
    unit_of_measure: str = "kg"
    default_bag_size_kg: float = 50


class ProductUpdateRequest(BaseModel):
    name: str | None = None
    category: str | None = None
    unit_of_measure: str | None = None
    default_bag_size_kg: float | None = None


class ProductStatusRequest(BaseModel):
    status: str  # active | discontinued


class FormulaLineRequest(BaseModel):
    material_id: int
    quantity_per_unit: float


class FormulaVersionRequest(BaseModel):
    effective_from: date
    lines: list[FormulaLineRequest]


class FinishedGoodsMovementRequest(BaseModel):
    delta_kg: float


class FormulaLineResponse(BaseModel):
    material_id: int
    material_name: str
    unit: str
    quantity_per_unit: float


class FormulaResponse(BaseModel):
    id: int
    product_id: int
    version: int
    effective_from: date
    is_active: bool
    created_at: datetime
    lines: list[FormulaLineResponse]


class FormulaVersionSummary(BaseModel):
    id: int
    version: int
    effective_from: date
    is_active: bool
    created_at: datetime


class FinishedGoodsResponse(BaseModel):
    product_id: int
    available_kg: float
    available_bags: int
    updated_at: datetime


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str | None
    unit_of_measure: str
    default_bag_size_kg: float
    status: str
    created_at: datetime
    active_formula: FormulaResponse | None = None
    formula_versions: list[FormulaVersionSummary] | None = None
    finished_goods: FinishedGoodsResponse | None = None


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int
