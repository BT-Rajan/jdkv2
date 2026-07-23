from perennia_search import PerenniaSearch
from perennia_notify import PerenniaNotify

from app.core.errors import AppError
from app.domain.inventory.repository import InventoryRepository
from app.domain.users.repository import UserAdminRepository
from app.permissions.definitions import SYSTEM_IDENTITY


class InventoryService:
    def __init__(self, repo: InventoryRepository, search: PerenniaSearch,
                 notify: PerenniaNotify, user_repo: UserAdminRepository):
        self._repo = repo
        self._search = search
        self._notify = notify
        self._user_repo = user_repo

    def create_material(self, identity, name: str, unit: str) -> dict:
        material_id = self._repo.create_material(name, unit)
        self._search.index("material", str(material_id), identity=SYSTEM_IDENTITY)
        return self._repo.get_material(material_id)

    def get(self, material_id: int) -> dict:
        material = self._repo.get_material(material_id)
        if not material:
            raise AppError("not_found")
        material["used_by_products"] = self._repo.products_using_material(material_id)
        material["recent_movements"] = self._repo.movement_history(material_id)
        return material

    def search(self, keyword, low_stock_only, limit, offset):
        return self._repo.search_materials(keyword, low_stock_only, limit, offset)

    def set_reorder_config(self, identity, material_id: int, minimum_stock: float,
                            reorder_point: float, lead_time_days: int) -> dict:
        if not self._repo.get_material(material_id):
            raise AppError("not_found")
        self._repo.set_reorder_config(material_id, minimum_stock, reorder_point, lead_time_days)
        return self.get(material_id)

    def record_movement(self, identity, material_id: int, movement_type: str,
                         quantity: float, reference: str | None) -> dict:
        material = self._repo.get_material(material_id)
        if not material:
            raise AppError("not_found")
        if movement_type not in ("receipt", "consumption", "adjustment"):
            raise AppError("validation_error")

        new_stock = self._repo.record_movement(
            material_id, movement_type, quantity, reference, identity.subject_id,
        )
        self._search.update("material", str(material_id), identity=SYSTEM_IDENTITY)

        if new_stock <= material["reorder_point"]:
            self._alert_low_stock(material["name"], material_id, new_stock, material["reorder_point"])

        return self.get(material_id)

    def _alert_low_stock(self, name: str, material_id: int, current_stock: float, reorder_point: float) -> None:
        # Recipients are resolved by role rather than hardcoded, since
        # perennia-access owns "who currently holds the procurement role".
        rows, _ = self._user_repo.search(keyword=None, status="active", role="procurement", limit=50, offset=0)
        for row in rows:
            self._notify.send(
                channel="email",
                recipient=row["email"],
                subject=f"Low stock: {name}",
                body=(
                    f"{name} (material #{material_id}) is at {current_stock}, "
                    f"at or below its reorder point of {reorder_point}."
                ),
                identity=SYSTEM_IDENTITY,
            )
