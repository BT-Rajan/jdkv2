from perennia_search import PerenniaSearch

from app.core.errors import AppError
from app.domain.products.repository import ProductRepository
from app.permissions.definitions import SYSTEM_IDENTITY


class ProductService:
    def __init__(self, repo: ProductRepository, search: PerenniaSearch):
        self._repo = repo
        self._search = search

    def create(self, identity, name: str, category: str | None, unit_of_measure: str,
               default_bag_size_kg: float) -> dict:
        product_id = self._repo.create(name, category, unit_of_measure, default_bag_size_kg)
        self._search.index("product", str(product_id), identity=SYSTEM_IDENTITY)
        return self.get(product_id)

    def update(self, identity, product_id: int, data: dict) -> dict:
        if not self._repo.get(product_id):
            raise AppError("not_found")
        self._repo.update(product_id, data)
        self._search.update("product", str(product_id), identity=SYSTEM_IDENTITY)
        return self.get(product_id)

    def set_status(self, identity, product_id: int, status: str) -> dict:
        if status not in ("active", "discontinued"):
            raise AppError("validation_error")
        if not self._repo.get(product_id):
            raise AppError("not_found")
        self._repo.set_status(product_id, status)
        self._search.update("product", str(product_id), identity=SYSTEM_IDENTITY)
        return self.get(product_id)

    def get(self, product_id: int) -> dict:
        product = self._repo.get(product_id)
        if not product:
            raise AppError("not_found")
        product["active_formula"] = self._repo.get_active_formula(product_id)
        product["formula_versions"] = self._repo.list_formula_versions(product_id)
        product["finished_goods"] = self._repo.get_finished_goods(product_id)
        return product

    def search(self, keyword, status, limit, offset):
        return self._repo.search(keyword, status, limit, offset)

    def create_formula_version(self, identity, product_id: int, effective_from, lines: list[dict]) -> dict:
        if not self._repo.get(product_id):
            raise AppError("not_found")
        if not lines:
            raise AppError("validation_error")
        self._repo.create_formula_version(product_id, effective_from, lines)
        self._search.update("product", str(product_id), identity=SYSTEM_IDENTITY)
        return self.get(product_id)

    def record_finished_goods_movement(self, identity, product_id: int, delta_kg: float) -> dict:
        product = self._repo.get(product_id)
        if not product:
            raise AppError("not_found")
        return self._repo.adjust_finished_goods(product_id, delta_kg, product["default_bag_size_kg"])
