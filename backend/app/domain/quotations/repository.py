import uuid
from datetime import datetime, timezone

from app.core.database import Database

QUOTATION_STATUSES = ("draft", "sent", "accepted", "rejected", "expired", "converted")


class QuotationRepository:
    def __init__(self, db: Database):
        self._db = db

    def _next_quote_no(self, cur) -> str:
        year = datetime.now(timezone.utc).year
        cur.execute("SELECT COUNT(*) AS n FROM quotations WHERE quote_no LIKE %s", (f"QT-{year}-%",))
        n = cur.fetchone()["n"] + 1
        return f"QT-{year}-{n:04d}"

    def create(self, chain_id: str, feasibility_id: str, customer_id: int, product_id: int,
               quantity_kg: float, unit_price: float, quote_date, valid_until,
               requested_delivery_date, terms: str | None, notes: str | None,
               created_by_subject_id: str) -> str:
        quote_id = str(uuid.uuid4())
        total_amount = round(unit_price * quantity_kg, 2)
        with self._db.transaction() as cur:
            quote_no = self._next_quote_no(cur)
            cur.execute(
                """
                INSERT INTO quotations
                    (id, chain_id, feasibility_id, quote_no, customer_id, product_id, quantity_kg,
                     unit_price, total_amount, quote_date, valid_until, requested_delivery_date,
                     terms, notes, status, created_by_subject_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'draft',%s)
                """,
                (quote_id, chain_id, feasibility_id, quote_no, customer_id, product_id, quantity_kg,
                 unit_price, total_amount, quote_date, valid_until, requested_delivery_date,
                 terms, notes, created_by_subject_id),
            )
        return quote_id

    def get(self, quote_id: str) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT q.*, c.name AS customer_name, p.name AS product_name
                FROM quotations q
                JOIN customers c ON c.id = q.customer_id
                JOIN products p ON p.id = q.product_id
                WHERE q.id = %s
                """,
                (quote_id,),
            )
            return cur.fetchone()

    def search(self, customer_id: int | None, status: str | None, limit: int, offset: int) -> tuple[list[dict], int]:
        clauses, params = [], []
        if customer_id:
            clauses.append("q.customer_id = %s")
            params.append(customer_id)
        if status:
            clauses.append("q.status = %s")
            params.append(status)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        base = f"""
            FROM quotations q
            JOIN customers c ON c.id = q.customer_id
            JOIN products p ON p.id = q.product_id
            {where_sql}
        """
        with self._db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total {base}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT q.*, c.name AS customer_name, p.name AS product_name {base} ORDER BY q.created_at DESC LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            return cur.fetchall(), total

    def update_terms(self, quote_id: str, data: dict) -> None:
        """Pricing/terms only - never customer_id, product_id or quantity_kg."""
        fields, params = [], []
        for col in ("unit_price", "valid_until", "terms", "notes"):
            if col in data:
                fields.append(f"{col} = %s")
                params.append(data[col])
        if "unit_price" in data:
            fields.append("total_amount = unit_price * quantity_kg")
        if not fields:
            return
        params.append(quote_id)
        with self._db.transaction() as cur:
            cur.execute(f"UPDATE quotations SET {', '.join(fields)} WHERE id = %s", params)

    def set_status(self, quote_id: str, status: str) -> None:
        with self._db.transaction() as cur:
            cur.execute("UPDATE quotations SET status = %s WHERE id = %s", (status, quote_id))

    def amend(self, quote_id: str, data: dict, amended_by_subject_id: str) -> None:
        fields, params = [], []
        for col in ("unit_price", "valid_until", "terms", "notes"):
            if col in data:
                fields.append(f"{col} = %s")
                params.append(data[col])
        if "unit_price" in data:
            fields.append("total_amount = unit_price * quantity_kg")
        if not fields:
            return
        fields.append("amended_at = NOW()")
        fields.append("amended_by_subject_id = %s")
        params.append(amended_by_subject_id)
        params.append(quote_id)
        with self._db.transaction() as cur:
            cur.execute(f"UPDATE quotations SET {', '.join(fields)} WHERE id = %s", params)
