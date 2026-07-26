from perennia_search import PerenniaSearch
from perennia_notify import PerenniaNotify

from app.core.errors import AppError
from app.domain.orders.repository import OrderRepository, ORDER_STATUSES
from app.domain.products.repository import ProductRepository
from app.domain.customers.repository import CustomerRepository
from app.permissions.definitions import SYSTEM_IDENTITY


class OrderService:
    def __init__(self, repo: OrderRepository, product_repo: ProductRepository,
                 customer_repo: CustomerRepository, search: PerenniaSearch, notify: PerenniaNotify):
        self._repo = repo
        self._product_repo = product_repo
        self._customer_repo = customer_repo
        self._search = search
        self._notify = notify

    def _availability(self, product_id: int, quantity_kg: float) -> dict:
        finished_goods = self._product_repo.get_finished_goods(product_id) or {"available_kg": 0}
        available_kg = float(finished_goods["available_kg"])
        shortfall_kg = max(0.0, quantity_kg - available_kg)
        return {
            "available_kg": available_kg,
            "required_kg": quantity_kg,
            "shortfall_kg": shortfall_kg,
            "fulfillable_from_stock": shortfall_kg == 0,
        }

    def create_from_quotation(self, identity, quotation: dict, order_date, delivery_date,
                               bag_size_kg: float, priority: str, notes: str | None) -> dict:
        """The only path that creates an order. customer_id, product_id and
        quantity_kg are taken from the accepted quotation, never from the
        caller, so an order can never diverge from what was quoted."""
        if order_date < quotation["quote_date"]:
            raise AppError("validation_error")
        if delivery_date <= order_date:
            raise AppError("validation_error")

        order_id = self._repo.create(
            quotation["customer_id"], quotation["product_id"], float(quotation["quantity_kg"]),
            bag_size_kg, delivery_date, priority, notes, identity.subject_id,
            chain_id=quotation["chain_id"], quotation_id=quotation["id"], order_date=order_date,
        )
        self._search.index("order", str(order_id), identity=SYSTEM_IDENTITY)
        return self.get(order_id)

    def update(self, identity, order_id: int, data: dict) -> dict:
        order = self._repo.get(order_id)
        if not order:
            raise AppError("not_found")

        effective_order_date = data.get("order_date", order["order_date"])
        effective_delivery_date = data.get("delivery_date", order["delivery_date"])
        if effective_order_date and effective_delivery_date and effective_delivery_date <= effective_order_date:
            raise AppError("validation_error")

        self._repo.update(order_id, data)
        self._search.update("order", str(order_id), identity=SYSTEM_IDENTITY)
        return self.get(order_id)

    def set_status(self, identity, order_id: int, status: str) -> dict:
        if status not in ORDER_STATUSES:
            raise AppError("validation_error")
        order = self._repo.get(order_id)
        if not order:
            raise AppError("not_found")

        self._repo.set_status(order_id, status)
        self._search.update("order", str(order_id), identity=SYSTEM_IDENTITY)

        if status in ("at_risk", "delayed", "cancelled"):
            # Ensure notify channels are registered before sending
            from app.core.security import _ensure_notify_channels
            _ensure_notify_channels()
            
            self._notify.send(
                channel="email",
                recipient=order.get("customer_email") or "operations@jdk.local",
                subject=f"Order {order['order_no']} is now {status}",
                body=f"Order {order['order_no']} for {order['customer_name']} changed to '{status}'.",
                identity=SYSTEM_IDENTITY,
            )
        return self.get(order_id)

    def get(self, order_id: int) -> dict:
        order = self._repo.get(order_id)
        if not order:
            raise AppError("not_found")
        order["availability"] = self._availability(order["product_id"], float(order["quantity_kg"]))
        return order

    def search(self, keyword, status, customer_id, limit, offset):
        return self._repo.search(keyword, status, customer_id, limit, offset)

    def check_availability(self, product_id: int, quantity_kg: float) -> dict:
        if not self._product_repo.get(product_id):
            raise AppError("not_found")
        return self._availability(product_id, quantity_kg)
