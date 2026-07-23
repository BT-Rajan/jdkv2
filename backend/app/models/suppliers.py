from datetime import datetime
from pydantic import BaseModel


class SupplierCreateRequest(BaseModel):
    name: str
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    gstin: str | None = None
    category: str | None = None
    rating: int | None = None
    notes: str | None = None


class SupplierUpdateRequest(BaseModel):
    name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    gstin: str | None = None
    category: str | None = None
    rating: int | None = None
    notes: str | None = None


class SupplyTermsRequest(BaseModel):
    material_id: int
    price: float
    lead_time_days: int
    minimum_order_qty: float
    payment_terms: str | None = None
    delivery_cost: float = 0


class MaterialSupplyTerm(BaseModel):
    id: int
    material_id: int
    material_name: str
    unit: str
    price: float
    lead_time_days: int
    minimum_order_qty: float
    payment_terms: str | None
    delivery_cost: float


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_person: str | None
    phone: str | None
    email: str | None
    address: str | None
    gstin: str | None
    category: str | None
    rating: int | None
    status: str
    notes: str | None
    created_at: datetime
    materials_supplied: list[MaterialSupplyTerm] | None = None


class SupplierListResponse(BaseModel):
    suppliers: list[SupplierResponse]
    total: int
