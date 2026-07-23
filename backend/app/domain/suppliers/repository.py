from app.core.database import Database


class SupplierRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, data: dict) -> int:
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO suppliers
                    (name, contact_person, phone, email, address, gstin, category, rating, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    data["name"], data.get("contact_person"), data.get("phone"),
                    data.get("email"), data.get("address"), data.get("gstin"),
                    data.get("category"), data.get("rating"), data.get("notes"),
                ),
            )
            return cur.lastrowid

    def update(self, supplier_id: int, data: dict) -> None:
        fields, params = [], []
        for col in ("name", "contact_person", "phone", "email", "address", "gstin", "category", "rating", "notes"):
            if col in data:
                fields.append(f"{col} = %s")
                params.append(data[col])
        if not fields:
            return
        params.append(supplier_id)
        with self._db.transaction() as cur:
            cur.execute(f"UPDATE suppliers SET {', '.join(fields)} WHERE id = %s", params)

    def deactivate(self, supplier_id: int) -> None:
        with self._db.transaction() as cur:
            cur.execute("UPDATE suppliers SET status = 'inactive' WHERE id = %s", (supplier_id,))

    def get(self, supplier_id: int) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))
            return cur.fetchone()

    def search(self, keyword: str | None, category: str | None, status: str | None,
               limit: int, offset: int) -> tuple[list[dict], int]:
        clauses, params = [], []
        if keyword:
            clauses.append("(name LIKE %s OR contact_person LIKE %s)")
            like = f"%{keyword}%"
            params.extend([like, like])
        if category:
            clauses.append("category = %s")
            params.append(category)
        if status:
            clauses.append("status = %s")
            params.append(status)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        with self._db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total FROM suppliers {where_sql}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT * FROM suppliers {where_sql} ORDER BY name LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            return cur.fetchall(), total

    def list_all_ids(self) -> list[int]:
        with self._db.cursor() as cur:
            cur.execute("SELECT id FROM suppliers")
            return [r["id"] for r in cur.fetchall()]

    # ---------------------------------------------------- material supply

    def upsert_supply_terms(self, material_id: int, supplier_id: int, price: float,
                             lead_time_days: int, minimum_order_qty: float,
                             payment_terms: str | None, delivery_cost: float) -> None:
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO raw_material_supply
                    (material_id, supplier_id, price, lead_time_days, minimum_order_qty,
                     payment_terms, delivery_cost)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    price = VALUES(price), lead_time_days = VALUES(lead_time_days),
                    minimum_order_qty = VALUES(minimum_order_qty),
                    payment_terms = VALUES(payment_terms), delivery_cost = VALUES(delivery_cost)
                """,
                (material_id, supplier_id, price, lead_time_days, minimum_order_qty,
                 payment_terms, delivery_cost),
            )

    def supply_terms_for_supplier(self, supplier_id: int) -> list[dict]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT s.id, rm.id AS material_id, rm.name AS material_name, rm.unit,
                       s.price, s.lead_time_days, s.minimum_order_qty, s.payment_terms, s.delivery_cost
                FROM raw_material_supply s
                JOIN raw_materials rm ON rm.id = s.material_id
                WHERE s.supplier_id = %s
                """,
                (supplier_id,),
            )
            return cur.fetchall()

    def suppliers_for_material(self, material_id: int) -> list[dict]:
        """Ranked cheapest-first - used by the MRP/ATP procurement suggestion."""
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT sup.id AS supplier_id, sup.name AS supplier_name, sup.rating,
                       s.price, s.lead_time_days, s.minimum_order_qty, s.payment_terms, s.delivery_cost
                FROM raw_material_supply s
                JOIN suppliers sup ON sup.id = s.supplier_id AND sup.status = 'active'
                WHERE s.material_id = %s
                ORDER BY s.price ASC
                """,
                (material_id,),
            )
            return cur.fetchall()
