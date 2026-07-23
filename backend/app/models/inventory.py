from datetime import datetime
from pydantic import BaseModel


class MaterialCreateRequest(BaseModel):
    name: str
    unit: str = "kg"


class ReorderConfigRequest(BaseModel):
    minimum_stock: float
    reorder_point: float
    lead_time_days: int


class MovementRequest(BaseModel):
    movement_type: str  # receipt | consumption | adjustment
    quantity: float
    reference: str | None = None


class ProductRef(BaseModel):
    id: int
    name: str


class MovementEntry(BaseModel):
    id: int
    movement_type: str
    quantity: float
    reference: str | None
    actor_subject_id: str | None
    created_at: datetime


class MaterialResponse(BaseModel):
    id: int
    name: str
    unit: str
    status: str
    current_stock: float
    minimum_stock: float
    reorder_point: float
    lead_time_days: int
    used_by_products: list[ProductRef] | None = None
    recent_movements: list[MovementEntry] | None = None


class MaterialListResponse(BaseModel):
    materials: list[MaterialResponse]
    total: int
