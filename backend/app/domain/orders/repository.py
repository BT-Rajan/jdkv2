import uuid
from datetime import datetime, timezone

from app.core.database import Database

ORDER_STATUSES = (
    "draft", "confirmed", "planned", "partially_fulfilled", "fulfilled",
    "at_risk", "delayed", "cancelled",
)


class OrderRepository:
    def __init__(self, db: Database):
        self._db = db

    def _next_order_no(self, cur) -> str:
        year = datetime.now(timezone.utc).year
        cur.execute(
            "SELECT COUNT(*) AS n FROM customer_orders WHERE order_no LIKE %s",
            (f"SO-{year}-%",),
        )
        n = cur.fetchone()["n"] + 1
        return f"SO-{year}-{n:04d}"

    def create(self, customer_id: int, product_id: int, quantity_kg: float,
               bag_size_kg: float, delivery_date, priority: str, notes: str | None,
               created_by_subject_id: str) -> int:
        with self._db.transaction() as cur:
            order_no = self._next_order_no(cur)
            bags = int(quantity_kg // bag_size_kg) if bag_size_kg else 0
            cur.execute(
                """
                INSERT INTO customer_orders
                    (order_no, customer_id, product_id, quantity_kg, bag_size_kg, bags,
                     delivery_date, priority, notes, created_by_subject_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (order_no, customer_id, product_id, quantity_kg, bag_size_kg, bags,
                 delivery_date, priority, notes, created_by_subject_id),
            )
            return cur.lastrowid

    def get(self, order_id: int) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT co.*, c.name AS customer_name, p.name AS product_name
                FROM customer_orders co
                JOIN customers c ON c.id = co.customer_id
                JOIN products p ON p.id = co.product_id
                WHERE co.id = %s
                """,
                (order_id,),
            )
            return cur.fetchone()

    def update(self, order_id: int, data: dict) -> None:
        fields, params = [], []
        for col in ("quantity_kg", "bag_size_kg", "bags", "delivery_date", "priority", "notes"):
            if col in data:
                fields.append(f"{col} = %s")
                params.append(data[col])
        if not fields:
            return
        params.append(order_id)
        with self._db.transaction() as cur:
            cur.execute(f"UPDATE customer_orders SET {', '.join(fields)} WHERE id = %s", params)

    def set_status(self, order_id: int, status: str) -> None:
        with self._db.transaction() as cur:
            cur.execute("UPDATE customer_orders SET status = %s WHERE id = %s", (status, order_id))

    def search(self, keyword: str | None, status: str | None, customer_id: int | None,
               limit: int, offset: int) -> tuple[list[dict], int]:
        clauses, params = [], []
        if keyword:
            clauses.append("(co.order_no LIKE %s OR c.name LIKE %s OR p.name LIKE %s)")
            like = f"%{keyword}%"
            params.extend([like, like, like])
        if status:
            clauses.append("co.status = %s")
            params.append(status)
        if customer_id:
            clauses.append("co.customer_id = %s")
            params.append(customer_id)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        base = f"""
            FROM customer_orders co
            JOIN customers c ON c.id = co.customer_id
            JOIN products p ON p.id = co.product_id
            {where_sql}
        """
        with self._db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total {base}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"""
                SELECT co.*, c.name AS customer_name, p.name AS product_name
                {base}
                ORDER BY co.delivery_date IS NULL, co.delivery_date ASC, co.created_at DESC
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            return cur.fetchall(), total

    def list_all_ids(self) -> list[int]:
        with self._db.cursor() as cur:
            cur.execute("SELECT id FROM customer_orders")
            return [r["id"] for r in cur.fetchall()]

    OPEN_STATUSES = ("draft", "confirmed", "planned", "partially_fulfilled", "at_risk", "delayed")

    def open_orders_by_product(self) -> dict[int, list[dict]]:
        """Groups every not-yet-fulfilled, not-cancelled order by product -
        the demand-side input to MRP (see docs/features/mrp-and-atp.md)."""
        placeholders = ",".join(["%s"] * len(self.OPEN_STATUSES))
        with self._db.cursor() as cur:
            cur.execute(
                f"""
                SELECT co.id, co.order_no, co.product_id, co.quantity_kg, co.delivery_date,
                       co.status, co.priority, c.name AS customer_name
                FROM customer_orders co
                JOIN customers c ON c.id = co.customer_id
                WHERE co.status IN ({placeholders})
                ORDER BY co.delivery_date IS NULL, co.delivery_date ASC
                """,
                self.OPEN_STATUSES,
            )
            by_product: dict[int, list[dict]] = {}
            for row in cur.fetchall():
                by_product.setdefault(row["product_id"], []).append(row)
            return by_product
