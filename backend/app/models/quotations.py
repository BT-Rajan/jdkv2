from datetime import date, datetime
from pydantic import BaseModel


class QuotationCreateRequest(BaseModel):
    feasibility_id: str
    unit_price: float
    valid_until: date | None = None
    terms: str | None = None
    notes: str | None = None


class QuotationUpdateRequest(BaseModel):
    """Only pricing/terms fields - customer, product and quantity are locked
    to the originating feasibility check for the life of the quotation."""
    unit_price: float | None = None
    valid_until: date | None = None
    terms: str | None = None
    notes: str | None = None


class QuotationStatusRequest(BaseModel):
    status: str  # sent | accepted | rejected | expired


class QuotationResponse(BaseModel):
    id: str
    chain_id: str
    feasibility_id: str
    quote_no: str
    customer_id: int
    customer_name: str
    product_id: int
    product_name: str
    quantity_kg: float
    unit_price: float
    total_amount: float
    quote_date: date
    valid_until: date | None
    requested_delivery_date: date
    terms: str | None
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    can_convert_to_order: bool


class QuotationListResponse(BaseModel):
    quotations: list[QuotationResponse]
    total: int


class ConvertToOrderRequest(BaseModel):
    order_date: date | None = None  # defaults to today; must be >= quote_date
    delivery_date: date  # must be strictly later than order_date
    bag_size_kg: float = 50
    priority: str = "normal"
    notes: str | None = None
