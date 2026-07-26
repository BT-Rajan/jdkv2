"""Customer persistence.

Create/get/update run through perennia-crud's CrudEngine (see schema.py) -
that's the "perennia-crud rebuild" for this entity. The OR-across-columns
keyword search and the order-history join aren't expressible through
perennia-crud's ListQuery (AND-only, single table), so those two stay as
direct SQL against JDK's own Database wrapper, same as before.
"""
from perennia_crud import CrudEngine
from perennia_crud.exceptions import RecordNotFoundError

from app.core.config import load_settings
from app.core.crud_config import build_crud_config
from app.core.database import Database
from app.domain.customers.schema import CUSTOMER_SCHEMA

_engine = CrudEngine(build_crud_config(load_settings()), CUSTOMER_SCHEMA)


class CustomerRepository:
    def __init__(self, db: Database):
        self._db = db
        self._engine = _engine

    def create(self, data: dict) -> int:
        record = self._engine.create(data)
        return record["id"]

    def update(self, customer_id: int, data: dict) -> None:
        if not data:
            return
        self._engine.update(customer_id, data)

    def deactivate(self, customer_id: int) -> None:
        self._engine.update(customer_id, {"status": "inactive"})

    def get(self, customer_id: int) -> dict | None:
        try:
            return self._engine.get(customer_id)
        except RecordNotFoundError:
            return None

    def search(self, keyword: str | None, status: str | None, limit: int, offset: int) -> tuple[list[dict], int]:
        clauses, params = [], []
        if keyword:
            clauses.append("(name LIKE %s OR contact_person LIKE %s OR email LIKE %s OR phone LIKE %s)")
            like = f"%{keyword}%"
            params.extend([like, like, like, like])
        if status:
            clauses.append("status = %s")
            params.append(status)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        with self._db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total FROM customers {where_sql}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT * FROM customers {where_sql} ORDER BY name LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            return cur.fetchall(), total

    def order_history(self, customer_id: int) -> list[dict]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT co.id, co.order_no, co.quantity_kg, co.delivery_date,
                       co.status, co.priority, p.name AS product_name
                FROM customer_orders co
                JOIN products p ON p.id = co.product_id
                WHERE co.customer_id = %s
                ORDER BY co.created_at DESC
                """,
                (customer_id,),
            )
            return cur.fetchall()

    def list_all_ids(self) -> list[int]:
        with self._db.cursor() as cur:
            cur.execute("SELECT id FROM customers")
            return [row["id"] for row in cur.fetchall()]
