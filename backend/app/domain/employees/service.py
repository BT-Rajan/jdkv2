from perennia_crud import CrudEngine, FilterCondition, ListQuery, SortField
from perennia_crud.exceptions import RecordNotFoundError

from app.core.config import load_settings
from app.core.crud_config import build_crud_config
from app.core.errors import AppError
from app.domain.employees.schema import EMPLOYEE_SCHEMA

_engine = CrudEngine(build_crud_config(load_settings()), EMPLOYEE_SCHEMA)


class EmployeeService:
    """No bespoke joins/receiving logic here (unlike customers/suppliers/
    materials) - a plain directory table maps onto perennia-crud directly,
    so this service is a thin pass-through rather than owning a
    repository.py of its own."""

    def __init__(self, engine: CrudEngine = _engine):
        self._engine = engine

    def create(self, identity, data: dict) -> dict:
        return self._engine.create(data)

    def update(self, identity, employee_id: int, data: dict) -> dict:
        if not data:
            return self.get(employee_id)
        try:
            return self._engine.update(employee_id, data)
        except RecordNotFoundError:
            raise AppError("not_found")

    def get(self, employee_id: int) -> dict:
        try:
            return self._engine.get(employee_id)
        except RecordNotFoundError:
            raise AppError("not_found")

    def delete(self, identity, employee_id: int) -> bool:
        try:
            return self._engine.delete(employee_id)
        except RecordNotFoundError:
            raise AppError("not_found")

    def search(self, keyword: str | None, role: str | None, limit: int, offset: int):
        filters = []
        if keyword:
            filters.append(FilterCondition("full_name", "like", f"%{keyword}%"))
        if role:
            filters.append(FilterCondition("role", "eq", role))

        # perennia-crud paginates by page number; JDK's API (matching every
        # other entity here) paginates by limit/offset. The conversion below
        # is exact as long as offset is a multiple of limit, which holds for
        # normal sequential paging from the frontend (offset = page * limit).
        result = self._engine.list(ListQuery(
            filters=filters, sort=[SortField("full_name")],
            page=(offset // limit) + 1 if limit else 1, page_size=limit,
        ))
        return result.items, result.total

