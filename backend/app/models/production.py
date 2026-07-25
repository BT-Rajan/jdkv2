from datetime import datetime
from pydantic import BaseModel, Field


class ProductionCycleUpsertRequest(BaseModel):
    """Defines how a single batch of ONE product is run on the floor.

    Raw material requirements are deliberately not part of this request -
    they're derived from the product's active formula x batch_size (see
    ProductionCycleService), so the formula stays the one place material
    composition is edited.
    """

    batch_size: float = Field(gt=0)
    batch_size_unit: str = "kg"
    time_per_batch_minutes: int = Field(gt=0)
    finished_products_per_batch: float = Field(gt=0)
    output_per_batch: float = Field(gt=0)
    output_per_batch_unit: str = "kg"
    manpower_required: int = Field(ge=0)
    machinery_required: str = ""
    special_requirements: str | None = None


class RawMaterialRequirementLine(BaseModel):
    material_id: int
    material_name: str
    unit: str
    quantity_per_batch: float


class ProductionCycleResponse(BaseModel):
    product_id: int
    batch_size: float
    batch_size_unit: str
    time_per_batch_minutes: int
    finished_products_per_batch: float
    output_per_batch: float
    output_per_batch_unit: str
    manpower_required: int
    machinery_required: str
    special_requirements: str | None
    raw_material_requirements: list[RawMaterialRequirementLine]
    has_active_formula: bool
    updated_at: datetime
