from perennia_search.provider import SearchProvider
from perennia_search.models import ProviderDocument

from app.domain.inventory.repository import InventoryRepository


class MaterialSearchProvider(SearchProvider):
    def __init__(self, repo: InventoryRepository):
        self._repo = repo

    def build_document(self, entity_id: str) -> ProviderDocument:
        material = self._repo.get_material(int(entity_id))
        if not material:
            raise ValueError(f"material {entity_id} not found")
        used_by = ", ".join(p["name"] for p in self._repo.products_using_material(int(entity_id)))
        return ProviderDocument(
            title=material["name"],
            content=f"Unit: {material['unit']}. Used in: {used_by or 'no active formulas'}.",
            metadata={"status": material["status"], "material_id": material["id"]},
        )

    def list_entity_ids(self):
        return [str(i) for i in self._repo.list_all_ids()]
