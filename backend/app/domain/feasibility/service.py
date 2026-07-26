from app.core.errors import AppError
from app.domain.feasibility.repository import FeasibilityRepository, OUTCOMES_ALLOWING_QUOTATION
from app.domain.customers.repository import CustomerRepository
from app.domain.products.repository import ProductRepository
from app.intelligence.feasibility_engine import FeasibilityEngine


class FeasibilityService:
    def __init__(self, repo: FeasibilityRepository, customer_repo: CustomerRepository,
                 product_repo: ProductRepository, engine: FeasibilityEngine):
        self._repo = repo
        self._customer_repo = customer_repo
        self._product_repo = product_repo
        self._engine = engine

    def _shape(self, row: dict) -> dict:
        row["can_generate_quotation"] = row["status"] == "open" and row["outcome"] in OUTCOMES_ALLOWING_QUOTATION
        return row

    def run(self, identity, customer_id: int, product_id: int, quantity_kg: float,
            requested_delivery_date, notes: str | None) -> dict:
        if not self._customer_repo.get(customer_id):
            raise AppError("not_found")
        if not self._product_repo.get(product_id):
            raise AppError("not_found")
        if quantity_kg <= 0:
            raise AppError("validation_error")

        result = self._engine.assess(product_id, quantity_kg, requested_delivery_date)
        run_id = self._repo.create(
            customer_id, product_id, quantity_kg, requested_delivery_date,
            result["outcome"], result["estimated_fulfillment_date"],
            result["promptly_available_kg"], result["remaining_kg"], result["constraints"],
            notes, identity.subject_id,
        )
        return self.get(run_id)

    def get(self, run_id: str) -> dict:
        row = self._repo.get(run_id)
        if not row:
            raise AppError("not_found")
        return self._shape(row)

    def search(self, customer_id, outcome, status, limit, offset):
        rows, total = self._repo.search(customer_id, outcome, status, limit, offset)
        return [self._shape(r) for r in rows], total

    def amend(self, identity, run_id: str, notes: str | None) -> dict:
        """Administrator-only correction of a finalized feasibility record.
        Only `notes` may be amended - outcome and figures are the record of
        what was actually assessed at the time and are never rewritten."""
        if not self._repo.get(run_id):
            raise AppError("not_found")
        self._repo.amend_notes(run_id, notes, identity.subject_id)
        return self.get(run_id)
