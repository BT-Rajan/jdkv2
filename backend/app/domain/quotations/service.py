from datetime import date

from app.core.errors import AppError
from app.domain.quotations.repository import QuotationRepository
from app.domain.feasibility.repository import FeasibilityRepository, OUTCOMES_ALLOWING_QUOTATION
from app.domain.orders.repository import OrderRepository


class QuotationService:
    def __init__(self, repo: QuotationRepository, feasibility_repo: FeasibilityRepository,
                 order_repo: OrderRepository):
        self._repo = repo
        self._feasibility_repo = feasibility_repo
        self._order_repo = order_repo

    def _shape(self, row: dict) -> dict:
        row["can_convert_to_order"] = row["status"] == "accepted"
        return row

    def create(self, identity, feasibility_id: str, unit_price: float, valid_until,
               terms: str | None, notes: str | None) -> dict:
        run = self._feasibility_repo.get(feasibility_id)
        if not run:
            raise AppError("not_found")
        if run["status"] != "open":
            # Already spent on another quotation, or superseded - a fresh
            # feasibility check is required rather than reusing a stale one.
            raise AppError("conflict")
        if run["outcome"] not in OUTCOMES_ALLOWING_QUOTATION:
            raise AppError("conflict")
        if unit_price <= 0:
            raise AppError("validation_error")

        quote_id = self._repo.create(
            run["chain_id"], feasibility_id, run["customer_id"], run["product_id"],
            float(run["quantity_kg"]), unit_price, date.today(), valid_until,
            run["requested_delivery_date"], terms, notes, identity.subject_id,
        )
        self._feasibility_repo.mark_converted(feasibility_id)
        return self.get(quote_id)

    def get(self, quote_id: str) -> dict:
        row = self._repo.get(quote_id)
        if not row:
            raise AppError("not_found")
        return self._shape(row)

    def search(self, customer_id, status, limit, offset):
        rows, total = self._repo.search(customer_id, status, limit, offset)
        return [self._shape(r) for r in rows], total

    def update(self, identity, quote_id: str, data: dict) -> dict:
        """Editable only while still a draft - once sent/accepted/etc. it is
        history and only amend() (administrator) may touch it."""
        row = self._repo.get(quote_id)
        if not row:
            raise AppError("not_found")
        if row["status"] != "draft":
            raise AppError("conflict")
        self._repo.update_terms(quote_id, data)
        return self.get(quote_id)

    def set_status(self, identity, quote_id: str, status: str) -> dict:
        if status not in ("sent", "accepted", "rejected", "expired"):
            raise AppError("validation_error")
        row = self._repo.get(quote_id)
        if not row:
            raise AppError("not_found")
        if row["status"] in ("converted", "rejected", "expired"):
            raise AppError("conflict")
        self._repo.set_status(quote_id, status)
        return self.get(quote_id)

    def mark_converted(self, quote_id: str) -> None:
        self._repo.set_status(quote_id, "converted")

    def amend(self, identity, quote_id: str, data: dict) -> dict:
        if not self._repo.get(quote_id):
            raise AppError("not_found")
        self._repo.amend(quote_id, data, identity.subject_id)
        return self.get(quote_id)
