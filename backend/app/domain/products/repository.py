from app.core.database import Database


class ProductRepository:
    def __init__(self, db: Database):
        self._db = db

    # ------------------------------------------------------------ products

    def create(self, name: str, category: str | None, unit_of_measure: str,
               default_bag_size_kg: float) -> int:
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO products (name, category, unit_of_measure, default_bag_size_kg)
                VALUES (%s,%s,%s,%s)
                """,
                (name, category, unit_of_measure, default_bag_size_kg),
            )
            product_id = cur.lastrowid
            cur.execute(
                "INSERT INTO finished_goods_inventory (product_id) VALUES (%s)",
                (product_id,),
            )
            return product_id

    def update(self, product_id: int, data: dict) -> None:
        fields, params = [], []
        for col in ("name", "category", "unit_of_measure", "default_bag_size_kg"):
            if col in data:
                fields.append(f"{col} = %s")
                params.append(data[col])
        if not fields:
            return
        params.append(product_id)
        with self._db.transaction() as cur:
            cur.execute(f"UPDATE products SET {', '.join(fields)} WHERE id = %s", params)

    def set_status(self, product_id: int, status: str) -> None:
        with self._db.transaction() as cur:
            cur.execute("UPDATE products SET status = %s WHERE id = %s", (status, product_id))

    def get(self, product_id: int) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            return cur.fetchone()

    def search(self, keyword: str | None, status: str | None, limit: int, offset: int) -> tuple[list[dict], int]:
        clauses, params = [], []
        if keyword:
            clauses.append("(name LIKE %s OR category LIKE %s)")
            like = f"%{keyword}%"
            params.extend([like, like])
        if status:
            clauses.append("status = %s")
            params.append(status)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        with self._db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total FROM products {where_sql}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"SELECT * FROM products {where_sql} ORDER BY name LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            return cur.fetchall(), total

    def list_all_ids(self) -> list[int]:
        with self._db.cursor() as cur:
            cur.execute("SELECT id FROM products")
            return [r["id"] for r in cur.fetchall()]

    # ------------------------------------------------------------ formulas

    def get_active_formula(self, product_id: int) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM formulas WHERE product_id = %s AND is_active = 1 "
                "ORDER BY version DESC LIMIT 1",
                (product_id,),
            )
            formula = cur.fetchone()
            if not formula:
                return None
            cur.execute(
                """
                SELECT fl.material_id, rm.name AS material_name, rm.unit, fl.quantity_per_unit
                FROM formula_lines fl
                JOIN raw_materials rm ON rm.id = fl.material_id
                WHERE fl.formula_id = %s
                """,
                (formula["id"],),
            )
            formula["lines"] = cur.fetchall()
            return formula

    def list_formula_versions(self, product_id: int) -> list[dict]:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT id, version, effective_from, is_active, created_at "
                "FROM formulas WHERE product_id = %s ORDER BY version DESC",
                (product_id,),
            )
            return cur.fetchall()

    def create_formula_version(self, product_id: int, effective_from,
                                lines: list[dict]) -> int:
        """Creates a new formula version and deactivates the previous one -
        formulas are versioned, never mutated in place (see docs/03-domain-model.md).
        """
        with self._db.transaction() as cur:
            cur.execute("SELECT COALESCE(MAX(version), 0) AS max_version FROM formulas WHERE product_id = %s",
                        (product_id,))
            next_version = cur.fetchone()["max_version"] + 1

            cur.execute("UPDATE formulas SET is_active = 0 WHERE product_id = %s", (product_id,))
            cur.execute(
                "INSERT INTO formulas (product_id, version, effective_from, is_active) "
                "VALUES (%s, %s, %s, 1)",
                (product_id, next_version, effective_from),
            )
            formula_id = cur.lastrowid
            for line in lines:
                cur.execute(
                    "INSERT INTO formula_lines (formula_id, material_id, quantity_per_unit) VALUES (%s,%s,%s)",
                    (formula_id, line["material_id"], line["quantity_per_unit"]),
                )
            return formula_id

    # ------------------------------------------------------- finished goods

    def get_finished_goods(self, product_id: int) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM finished_goods_inventory WHERE product_id = %s", (product_id,))
            return cur.fetchone()

    def adjust_finished_goods(self, product_id: int, delta_kg: float, bag_size_kg: float) -> dict:
        with self._db.transaction() as cur:
            cur.execute(
                "UPDATE finished_goods_inventory SET available_kg = available_kg + %s WHERE product_id = %s",
                (delta_kg, product_id),
            )
            cur.execute("SELECT available_kg FROM finished_goods_inventory WHERE product_id = %s", (product_id,))
            available_kg = cur.fetchone()["available_kg"]
            available_bags = int(available_kg // bag_size_kg) if bag_size_kg else 0
            cur.execute(
                "UPDATE finished_goods_inventory SET available_bags = %s WHERE product_id = %s",
                (available_bags, product_id),
            )
            return {"available_kg": available_kg, "available_bags": available_bags}
