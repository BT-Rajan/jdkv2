from datetime import datetime, date
from pydantic import BaseModel


class CustomerCreateRequest(BaseModel):
    name: str
    client_type: str | None = None
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    delivery_address: str | None = None
    billing_address: str | None = None  # leave blank if same as delivery
    tax_id: str | None = None
    payment_terms: str | None = None
    credit_limit: float = 0
    notes: str | None = None


class CustomerUpdateRequest(BaseModel):
    name: str | None = None
    client_type: str | None = None
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    delivery_address: str | None = None
    billing_address: str | None = None
    tax_id: str | None = None
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
    client_type: str | None
    contact_person: str | None
    email: str | None
    phone: str | None
    delivery_address: str | None
    billing_address: str | None
    tax_id: str | None
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
