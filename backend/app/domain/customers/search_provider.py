from perennia_search.provider import SearchProvider
from perennia_search.models import ProviderDocument

from app.domain.customers.repository import CustomerRepository


class CustomerSearchProvider(SearchProvider):
    def __init__(self, repo: CustomerRepository):
        self._repo = repo

    def build_document(self, entity_id: str) -> ProviderDocument:
        customer = self._repo.get(int(entity_id))
        if not customer:
            raise ValueError(f"customer {entity_id} not found")
        content = " ".join(filter(None, [
            customer.get("contact_person"), customer.get("email"),
            customer.get("phone"), customer.get("address"), customer.get("gstin"),
        ]))
        return ProviderDocument(
            title=customer["name"],
            content=content,
            metadata={"status": customer["status"], "customer_id": customer["id"]},
        )

    def list_entity_ids(self):
        return [str(i) for i in self._repo.list_all_ids()]
