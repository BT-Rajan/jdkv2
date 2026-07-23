from datetime import date
from pydantic import BaseModel


class ContributingOrder(BaseModel):
    order_id: int
    order_no: str
    customer_name: str
    quantity_kg: float
    delivery_date: date | None


class ProductionRequirement(BaseModel):
    product_id: int
    product_name: str
    total_ordered_kg: float
    finished_goods_kg: float
    production_required_kg: float
    has_active_formula: bool
    contributing_orders: list[ContributingOrder]


class SuggestedSupplier(BaseModel):
    supplier_id: int
    supplier_name: str
    price: float
    lead_time_days: int
    minimum_order_qty: float
    is_projected: bool


class MaterialRequirement(BaseModel):
    material_id: int
    material_name: str
    unit: str
    gross_required: float
    current_stock: float
    net_required: float
    shortage: bool
    affected_product_ids: list[int]
    suggested_supplier: SuggestedSupplier | None
    estimated_supply_date: date | None


class MrpSnapshot(BaseModel):
    production_requirements: list[ProductionRequirement]
    material_requirements: list[MaterialRequirement]
    has_shortages: bool


class AtpConstraint(BaseModel):
    material_id: int | None = None
    material_name: str | None = None
    shortage: float | None = None
    unit: str | None = None
    supplier_lead_time_days: int | None = None
    is_projected: bool | None = None
    reason: str | None = None
    detail: str | None = None


class AtpResult(BaseModel):
    product_id: int
    requested_kg: float
    promptly_available_kg: float
    remaining_kg: float
    can_fully_promise_now: bool
    constraints: list[AtpConstraint]
    estimated_fulfillment_date: date
