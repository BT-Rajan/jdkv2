from app.core.database import Database


class CustomerRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, data: dict) -> int:
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO customers
                    (name, contact_person, email, phone, address, billing_address,
                     gstin, payment_terms, credit_limit, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    data["name"], data.get("contact_person"), data.get("email"),
                    data.get("phone"), data.get("address"), data.get("billing_address"),
                    data.get("gstin"), data.get("payment_terms"),
                    data.get("credit_limit", 0), data.get("notes"),
                ),
            )
            return cur.lastrowid

    def update(self, customer_id: int, data: dict) -> None:
        fields, params = [], []
        for col in ("name", "contact_person", "email", "phone", "address", "billing_address",
                    "gstin", "payment_terms", "credit_limit", "notes"):
            if col in data:
                fields.append(f"{col} = %s")
                params.append(data[col])
        if not fields:
            return
        params.append(customer_id)
        with self._db.transaction() as cur:
            cur.execute(f"UPDATE customers SET {', '.join(fields)} WHERE id = %s", params)

    def deactivate(self, customer_id: int) -> None:
        with self._db.transaction() as cur:
            cur.execute("UPDATE customers SET status = 'inactive' WHERE id = %s", (customer_id,))

    def get(self, customer_id: int) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
            return cur.fetchone()

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
