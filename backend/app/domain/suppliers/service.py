from perennia_search import PerenniaSearch

from app.core.errors import AppError
from app.domain.suppliers.repository import SupplierRepository
from app.permissions.definitions import SYSTEM_IDENTITY


class SupplierService:
    def __init__(self, repo: SupplierRepository, search: PerenniaSearch):
        self._repo = repo
        self._search = search

    def create(self, identity, data: dict) -> dict:
        supplier_id = self._repo.create(data)
        self._search.index("supplier", str(supplier_id), identity=SYSTEM_IDENTITY)
        return self.get(supplier_id)

    def update(self, identity, supplier_id: int, data: dict) -> dict:
        if not self._repo.get(supplier_id):
            raise AppError("not_found")
        self._repo.update(supplier_id, data)
        self._search.update("supplier", str(supplier_id), identity=SYSTEM_IDENTITY)
        return self.get(supplier_id)

    def deactivate(self, identity, supplier_id: int) -> dict:
        if not self._repo.get(supplier_id):
            raise AppError("not_found")
        self._repo.deactivate(supplier_id)
        self._search.update("supplier", str(supplier_id), identity=SYSTEM_IDENTITY)
        return self.get(supplier_id)

    def get(self, supplier_id: int) -> dict:
        supplier = self._repo.get(supplier_id)
        if not supplier:
            raise AppError("not_found")
        supplier["materials_supplied"] = self._repo.supply_terms_for_supplier(supplier_id)
        return supplier

    def search(self, keyword, category, status, limit, offset):
        return self._repo.search(keyword, category, status, limit, offset)

    def set_supply_terms(self, identity, material_id: int, supplier_id: int, price: float,
                          lead_time_days: int, minimum_order_qty: float,
                          payment_terms: str | None, delivery_cost: float) -> dict:
        if not self._repo.get(supplier_id):
            raise AppError("not_found")
        self._repo.upsert_supply_terms(
            material_id, supplier_id, price, lead_time_days,
            minimum_order_qty, payment_terms, delivery_cost,
        )
        self._search.update("supplier", str(supplier_id), identity=SYSTEM_IDENTITY)
        return self.get(supplier_id)
