"""
Registers each business domain's SearchProvider with perennia-search.

perennia-search has no idea what a "customer" or "product" is - each domain
supplies a SearchProvider that knows how to build a searchable projection of
its own entities (see app/domain/customers/search_provider.py for the
pattern). This module is the single place those registrations happen, so
main.py's startup hook stays a one-line call regardless of how many domains
register a provider.
"""
from perennia_search import PerenniaSearch

from app.core.database import Database
from app.core.config import load_settings
from app.domain.customers.repository import CustomerRepository
from app.domain.customers.search_provider import CustomerSearchProvider
from app.domain.inventory.repository import InventoryRepository
from app.domain.inventory.search_provider import MaterialSearchProvider
from app.domain.suppliers.repository import SupplierRepository
from app.domain.suppliers.search_provider import SupplierSearchProvider
from app.domain.products.repository import ProductRepository
from app.domain.products.search_provider import ProductSearchProvider
from app.domain.orders.repository import OrderRepository
from app.domain.orders.search_provider import OrderSearchProvider
from app.permissions.definitions import SYSTEM_IDENTITY


def register_all(search: PerenniaSearch) -> None:
    db = Database(load_settings())

    existing_codes = {r.code for r in search.list_resources(identity=SYSTEM_IDENTITY)}

    if "customer" not in existing_codes:
        search.register_resource(
            "customer", CustomerSearchProvider(CustomerRepository(db)),
            description="Customer records", identity=SYSTEM_IDENTITY,
        )

    if "material" not in existing_codes:
        search.register_resource(
            "material", MaterialSearchProvider(InventoryRepository(db)),
            description="Raw materials", identity=SYSTEM_IDENTITY,
        )

    if "supplier" not in existing_codes:
        search.register_resource(
            "supplier", SupplierSearchProvider(SupplierRepository(db)),
            description="Suppliers", identity=SYSTEM_IDENTITY,
        )

    if "product" not in existing_codes:
        search.register_resource(
            "product", ProductSearchProvider(ProductRepository(db)),
            description="Products and formulas", identity=SYSTEM_IDENTITY,
        )

    if "order" not in existing_codes:
        search.register_resource(
            "order", OrderSearchProvider(OrderRepository(db)),
            description="Customer orders", identity=SYSTEM_IDENTITY,
        )
