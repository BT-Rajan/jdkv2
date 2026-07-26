from app.core.errors import AppError
from app.domain.deliveries.repository import DeliveryRepository
from app.domain.orders.repository import OrderRepository


class DeliveryService:
    def __init__(self, repo: DeliveryRepository, order_repo: OrderRepository):
        self._repo = repo
        self._order_repo = order_repo

    def create(self, identity, order_id: int, delivery_date, dispatched_qty_kg: float,
               carrier: str | None, tracking_ref: str | None, notes: str | None) -> dict:
        order = self._order_repo.get(order_id)
        if not order:
            raise AppError("not_found")
        if order["status"] == "cancelled":
            raise AppError("conflict")
        if dispatched_qty_kg <= 0:
            raise AppError("validation_error")

        delivery_id = self._repo.create(
            order["chain_id"], order_id, delivery_date, dispatched_qty_kg,
            carrier, tracking_ref, notes, identity.subject_id,
        )
        return self.get(delivery_id)

    def get(self, delivery_id: str) -> dict:
        row = self._repo.get(delivery_id)
        if not row:
            raise AppError("not_found")
        return row

    def search(self, order_id, status, limit, offset):
        return self._repo.search(order_id, status, limit, offset)

    def set_status(self, identity, delivery_id: str, status: str) -> dict:
        if status not in ("dispatched", "delivered", "cancelled"):
            raise AppError("validation_error")
        row = self._repo.get(delivery_id)
        if not row:
            raise AppError("not_found")
        if row["status"] in ("delivered", "cancelled"):
            raise AppError("conflict")
        self._repo.set_status(delivery_id, status)
        return self.get(delivery_id)

    def amend(self, identity, delivery_id: str, data: dict) -> dict:
        if not self._repo.get(delivery_id):
            raise AppError("not_found")
        self._repo.amend(delivery_id, data, identity.subject_id)
        return self.get(delivery_id)
