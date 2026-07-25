from app.core.errors import AppError
from app.domain.production.repository import ProductionCycleRepository
from app.domain.products.repository import ProductRepository


class ProductionCycleService:
    def __init__(self, repo: ProductionCycleRepository, products: ProductRepository):
        self._repo = repo
        self._products = products

    def get(self, product_id: int) -> dict:
        if not self._products.get(product_id):
            raise AppError("not_found")
        cycle = self._repo.get(product_id)
        if not cycle:
            raise AppError("not_found")
        return self._with_materials(cycle)

    def upsert(self, product_id: int, data: dict) -> dict:
        if not self._products.get(product_id):
            raise AppError("not_found")
        self._repo.upsert(product_id, data)
        return self._with_materials(self._repo.get(product_id))

    def _with_materials(self, cycle: dict) -> dict:
        product_id = cycle["product_id"]
        cycle["raw_material_requirements"] = self._repo.raw_material_requirements(
            product_id, float(cycle["batch_size"]),
        )
        cycle["has_active_formula"] = self._repo.has_active_formula(product_id)
        return cycle
