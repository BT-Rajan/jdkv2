from perennia_search.provider import SearchProvider
from perennia_search.models import ProviderDocument

from app.domain.orders.repository import OrderRepository


class OrderSearchProvider(SearchProvider):
    def __init__(self, repo: OrderRepository):
        self._repo = repo

    def build_document(self, entity_id: str) -> ProviderDocument:
        order = self._repo.get(int(entity_id))
        if not order:
            raise ValueError(f"order {entity_id} not found")
        return ProviderDocument(
            title=f"{order['order_no']} — {order['customer_name']}",
            content=f"Product: {order['product_name']}. Status: {order['status']}. Priority: {order['priority']}.",
            metadata={"status": order["status"], "order_id": order["id"], "customer_id": order["customer_id"]},
        )

    def list_entity_ids(self):
        return [str(i) for i in self._repo.list_all_ids()]
