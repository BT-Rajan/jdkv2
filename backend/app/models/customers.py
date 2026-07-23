from datetime import datetime, date
from pydantic import BaseModel


class CustomerCreateRequest(BaseModel):
    name: str
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    billing_address: str | None = None
    gstin: str | None = None
    payment_terms: str | None = None
    credit_limit: float = 0
    notes: str | None = None


class CustomerUpdateRequest(BaseModel):
    name: str | None = None
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    billing_address: str | None = None
    gstin: str | None = None
    payment_terms: str | None = None
    credit_limit: float | None = None
    notes: str | None = None


class OrderHistoryEntry(BaseModel):
    id: int
    order_no: str
    quantity_kg: float
    delivery_date: date | None
    status: str
    priority: str
    product_name: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    contact_person: str | None
    email: str | None
    phone: str | None
    address: str | None
    billing_address: str | None
    gstin: str | None
    payment_terms: str | None
    credit_limit: float
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    orders: list[OrderHistoryEntry] | None = None


class CustomerListResponse(BaseModel):
    customers: list[CustomerResponse]
    total: int
