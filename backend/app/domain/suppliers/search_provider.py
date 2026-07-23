from perennia_search.provider import SearchProvider
from perennia_search.models import ProviderDocument

from app.domain.suppliers.repository import SupplierRepository


class SupplierSearchProvider(SearchProvider):
    def __init__(self, repo: SupplierRepository):
        self._repo = repo

    def build_document(self, entity_id: str) -> ProviderDocument:
        supplier = self._repo.get(int(entity_id))
        if not supplier:
            raise ValueError(f"supplier {entity_id} not found")
        materials = ", ".join(t["material_name"] for t in self._repo.supply_terms_for_supplier(int(entity_id)))
        content = " ".join(filter(None, [
            supplier.get("contact_person"), supplier.get("phone"), supplier.get("email"),
            supplier.get("category"), materials,
        ]))
        return ProviderDocument(
            title=supplier["name"],
            content=content,
            metadata={"status": supplier["status"], "supplier_id": supplier["id"]},
        )

    def list_entity_ids(self):
        return [str(i) for i in self._repo.list_all_ids()]
