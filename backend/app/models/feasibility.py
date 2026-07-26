from datetime import date, datetime
from pydantic import BaseModel


class FeasibilityRunRequest(BaseModel):
    customer_id: int
    product_id: int
    quantity_kg: float
    requested_delivery_date: date
    notes: str | None = None


class FeasibilityConstraint(BaseModel):
    material_id: int | None = None
    material_name: str | None = None
    shortage: float | None = None
    supplier_lead_time_days: int | None = None


class FeasibilityRunResponse(BaseModel):
    id: str
    chain_id: str
    customer_id: int
    customer_name: str
    product_id: int
    product_name: str
    quantity_kg: float
    requested_delivery_date: date
    outcome: str
    estimated_fulfillment_date: date | None
    promptly_available_kg: float
    remaining_kg: float
    constraints: list[dict]
    status: str
    notes: str | None
    created_at: datetime
    can_generate_quotation: bool


class FeasibilityListResponse(BaseModel):
    runs: list[FeasibilityRunResponse]
    total: int


class FeasibilityAmendRequest(BaseModel):
    notes: str | None = None
