import uuid
from datetime import datetime, timezone

from app.core.database import Database

DELIVERY_STATUSES = ("scheduled", "dispatched", "delivered", "cancelled")


class DeliveryRepository:
    def __init__(self, db: Database):
        self._db = db

    def _next_delivery_no(self, cur) -> str:
        year = datetime.now(timezone.utc).year
        cur.execute("SELECT COUNT(*) AS n FROM deliveries WHERE delivery_no LIKE %s", (f"DL-{year}-%",))
        n = cur.fetchone()["n"] + 1
        return f"DL-{year}-{n:04d}"

    def create(self, chain_id: str, order_id: int, delivery_date, dispatched_qty_kg: float,
               carrier: str | None, tracking_ref: str | None, notes: str | None,
               created_by_subject_id: str) -> str:
        delivery_id = str(uuid.uuid4())
        with self._db.transaction() as cur:
            delivery_no = self._next_delivery_no(cur)
            cur.execute(
                """
                INSERT INTO deliveries
                    (id, chain_id, order_id, delivery_no, delivery_date, dispatched_qty_kg,
                     carrier, tracking_ref, notes, status, created_by_subject_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'scheduled',%s)
                """,
                (delivery_id, chain_id, order_id, delivery_no, delivery_date, dispatched_qty_kg,
                 carrier, tracking_ref, notes, created_by_subject_id),
            )
        return delivery_id

    def get(self, delivery_id: str) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT d.*, o.order_no
                FROM deliveries d
                JOIN customer_orders o ON o.id = d.order_id
                WHERE d.id = %s
                """,
                (delivery_id,),
            )
            return cur.fetchone()

    def search(self, order_id: int | None, status: str | None, limit: int, offset: int) -> tuple[list[dict], int]:
        clauses, params = [], []
        if order_id:
            clauses.append("d.order_id = %s")
            params.append(order_id)
        if status:
            clauses.append("d.status = %s")
            params.append(status)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        base = f"""
            FROM deliveries d
            JOIN customer_orders o ON o.id = d.order_id
            {where_sql}
        """
        with self._db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total {base}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT d.*, o.order_no {base} ORDER BY d.created_at DESC LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            return cur.fetchall(), total

    def set_status(self, delivery_id: str, status: str) -> None:
        with self._db.transaction() as cur:
            cur.execute("UPDATE deliveries SET status = %s WHERE id = %s", (status, delivery_id))

    def amend(self, delivery_id: str, data: dict, amended_by_subject_id: str) -> None:
        fields, params = [], []
        for col in ("delivery_date", "dispatched_qty_kg", "carrier", "tracking_ref", "notes"):
            if col in data:
                fields.append(f"{col} = %s")
                params.append(data[col])
        if not fields:
            return
        fields.append("amended_at = NOW()")
        fields.append("amended_by_subject_id = %s")
        params.append(amended_by_subject_id)
        params.append(delivery_id)
        with self._db.transaction() as cur:
            cur.execute(f"UPDATE deliveries SET {', '.join(fields)} WHERE id = %s", params)
