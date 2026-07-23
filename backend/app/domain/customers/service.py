from perennia_search import PerenniaSearch

from app.core.errors import AppError
from app.domain.customers.repository import CustomerRepository
from app.permissions.definitions import SYSTEM_IDENTITY


class CustomerService:
    def __init__(self, repo: CustomerRepository, search: PerenniaSearch):
        self._repo = repo
        self._search = search

    def create(self, identity, data: dict) -> dict:
        customer_id = self._repo.create(data)
        self._search.index("customer", str(customer_id), identity=SYSTEM_IDENTITY)
        return self._repo.get(customer_id)

    def update(self, identity, customer_id: int, data: dict) -> dict:
        if not self._repo.get(customer_id):
            raise AppError("not_found")
        self._repo.update(customer_id, data)
        self._search.update("customer", str(customer_id), identity=SYSTEM_IDENTITY)
        return self._repo.get(customer_id)

    def deactivate(self, identity, customer_id: int) -> dict:
        if not self._repo.get(customer_id):
            raise AppError("not_found")
        self._repo.deactivate(customer_id)
        self._search.update("customer", str(customer_id), identity=SYSTEM_IDENTITY)
        return self._repo.get(customer_id)

    def get(self, customer_id: int) -> dict:
        customer = self._repo.get(customer_id)
        if not customer:
            raise AppError("not_found")
        customer["orders"] = self._repo.order_history(customer_id)
        return customer

    def search(self, keyword, status, limit, offset):
        return self._repo.search(keyword, status, limit, offset)
