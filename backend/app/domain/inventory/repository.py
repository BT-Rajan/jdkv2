from app.core.database import Database


class InventoryRepository(object):
    def __init__(self, db: Database):
        self._db = db

    # ------------------------------------------------------------ materials

    def create_material(self, name: str, unit: str) -> int:
        with self._db.transaction() as cur:
            cur.execute("INSERT INTO raw_materials (name, unit) VALUES (%s,%s)", (name, unit))
            material_id = cur.lastrowid
            cur.execute(
                "INSERT INTO raw_material_inventory (material_id) VALUES (%s)",
                (material_id,),
            )
            return material_id

    def get_material(self, material_id: int) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT rm.id, rm.name, rm.unit, rm.status,
                       inv.current_stock, inv.minimum_stock, inv.reorder_point, inv.lead_time_days
                FROM raw_materials rm
                LEFT JOIN raw_material_inventory inv ON inv.material_id = rm.id
                WHERE rm.id = %s
                """,
                (material_id,),
            )
            return cur.fetchone()

    def search_materials(self, keyword: str | None, low_stock_only: bool,
                          limit: int, offset: int) -> tuple[list[dict], int]:
        clauses, params = ["rm.status = 'active'"], []
        if keyword:
            clauses.append("rm.name LIKE %s")
            params.append(f"%{keyword}%")
        if low_stock_only:
            clauses.append("inv.current_stock <= inv.reorder_point")
        where_sql = f"WHERE {' AND '.join(clauses)}"

        base = f"""
            FROM raw_materials rm
            LEFT JOIN raw_material_inventory inv ON inv.material_id = rm.id
            {where_sql}
        """
        with self._db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total {base}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"""
                SELECT rm.id, rm.name, rm.unit, rm.status,
                       inv.current_stock, inv.minimum_stock, inv.reorder_point, inv.lead_time_days
                {base}
                ORDER BY rm.name LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            return cur.fetchall(), total

    def set_reorder_config(self, material_id: int, minimum_stock: float,
                            reorder_point: float, lead_time_days: int) -> None:
        with self._db.transaction() as cur:
            cur.execute(
                """
                UPDATE raw_material_inventory
                SET minimum_stock = %s, reorder_point = %s, lead_time_days = %s
                WHERE material_id = %s
                """,
                (minimum_stock, reorder_point, lead_time_days, material_id),
            )

    def list_all_ids(self) -> list[int]:
        with self._db.cursor() as cur:
            cur.execute("SELECT id FROM raw_materials")
            return [r["id"] for r in cur.fetchall()]

    # ------------------------------------------------------------ movements

    def record_movement(self, material_id: int, movement_type: str, quantity: float,
                         reference: str | None, actor_subject_id: str | None) -> float:
        """Records a movement and updates the cached current_stock.
        `quantity` is signed for adjustments (+/-); receipts are always
        positive, consumption is always recorded positive but subtracts.
        Returns the new current_stock.
        """
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO inventory_movements
                    (material_id, movement_type, quantity, reference, actor_subject_id)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (material_id, movement_type, quantity, reference, actor_subject_id),
            )
            if movement_type == "consumption":
                delta = -abs(quantity)
            elif movement_type == "receipt":
                delta = abs(quantity)
            else:  # adjustment - signed as given
                delta = quantity

            cur.execute(
                "UPDATE raw_material_inventory SET current_stock = current_stock + %s WHERE material_id = %s",
                (delta, material_id),
            )
            cur.execute(
                "SELECT current_stock FROM raw_material_inventory WHERE material_id = %s",
                (material_id,),
            )
            return cur.fetchone()["current_stock"]

    def movement_history(self, material_id: int, limit: int = 50) -> list[dict]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT id, movement_type, quantity, reference, actor_subject_id, created_at
                FROM inventory_movements
                WHERE material_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (material_id, limit),
            )
            return cur.fetchall()

    # ------------------------------------------------------- product usage

    def products_using_material(self, material_id: int) -> list[dict]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT p.id, p.name
                FROM formula_lines fl
                JOIN formulas f ON f.id = fl.formula_id AND f.is_active = 1
                JOIN products p ON p.id = f.product_id
                WHERE fl.material_id = %s
                """,
                (material_id,),
            )
            return cur.fetchall()
