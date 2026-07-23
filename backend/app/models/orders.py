from datetime import date, datetime
from pydantic import BaseModel


class OrderCreateRequest(BaseModel):
    customer_id: int
    product_id: int
    quantity_kg: float
    bag_size_kg: float = 50
    delivery_date: date | None = None
    priority: str = "normal"  # critical | high | normal | low
    notes: str | None = None


class OrderUpdateRequest(BaseModel):
    quantity_kg: float | None = None
    bag_size_kg: float | None = None
    delivery_date: date | None = None
    priority: str | None = None
    notes: str | None = None


class OrderStatusRequest(BaseModel):
    status: str


class AvailabilityResponse(BaseModel):
    available_kg: float
    required_kg: float
    shortfall_kg: float
    fulfillable_from_stock: bool


class OrderResponse(BaseModel):
    id: int
    order_no: str
    customer_id: int
    customer_name: str
    product_id: int
    product_name: str
    quantity_kg: float
    bag_size_kg: float
    bags: int
    delivery_date: date | None
    status: str
    priority: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    availability: AvailabilityResponse | None = None


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
