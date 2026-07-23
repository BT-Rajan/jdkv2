from perennia_search.provider import SearchProvider
from perennia_search.models import ProviderDocument

from app.domain.products.repository import ProductRepository


class ProductSearchProvider(SearchProvider):
    def __init__(self, repo: ProductRepository):
        self._repo = repo

    def build_document(self, entity_id: str) -> ProviderDocument:
        product = self._repo.get(int(entity_id))
        if not product:
            raise ValueError(f"product {entity_id} not found")
        formula = self._repo.get_active_formula(int(entity_id))
        materials = ", ".join(l["material_name"] for l in formula["lines"]) if formula else ""
        return ProviderDocument(
            title=product["name"],
            content=f"Category: {product.get('category') or ''}. Materials: {materials}.",
            metadata={"status": product["status"], "product_id": product["id"]},
        )

    def list_entity_ids(self):
        return [str(i) for i in self._repo.list_all_ids()]
