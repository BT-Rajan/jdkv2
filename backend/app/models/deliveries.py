from datetime import date, datetime
from pydantic import BaseModel


class DeliveryCreateRequest(BaseModel):
    order_id: int
    delivery_date: date
    dispatched_qty_kg: float
    carrier: str | None = None
    tracking_ref: str | None = None
    notes: str | None = None


class DeliveryStatusRequest(BaseModel):
    status: str  # dispatched | delivered | cancelled


class DeliveryResponse(BaseModel):
    id: str
    chain_id: str
    order_id: int
    order_no: str
    delivery_no: str
    delivery_date: date
    dispatched_qty_kg: float
    carrier: str | None
    tracking_ref: str | None
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class DeliveryListResponse(BaseModel):
    deliveries: list[DeliveryResponse]
    total: int
