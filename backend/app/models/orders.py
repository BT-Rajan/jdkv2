from datetime import date, datetime
from pydantic import BaseModel


class OrderUpdateRequest(BaseModel):
    # customer_id and product_id are deliberately absent: they are fixed at
    # the quotation stage and never editable on an order.
    quantity_kg: float | None = None
    bag_size_kg: float | None = None
    order_date: date | None = None
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
    chain_id: str | None = None
    quotation_id: str | None = None
    order_date: date | None = None
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
