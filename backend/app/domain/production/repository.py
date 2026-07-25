from app.core.database import Database


class ProductionCycleRepository:
    """Per-product production cycle (batch size, timing, labour, machinery).

    One row per product - a cycle is edited in place rather than versioned
    like a formula, since (unlike material composition) past production
    runs don't need to stay traceable to the exact cycle parameters that
    were in effect at the time.
    """

    def __init__(self, db: Database):
        self._db = db

    def get(self, product_id: int) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM product_production_cycles WHERE product_id = %s",
                (product_id,),
            )
            return cur.fetchone()

    def upsert(self, product_id: int, data: dict) -> None:
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO product_production_cycles (
                    product_id, batch_size, batch_size_unit, time_per_batch_minutes,
                    finished_products_per_batch, output_per_batch, output_per_batch_unit,
                    manpower_required, machinery_required, special_requirements
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    batch_size = VALUES(batch_size),
                    batch_size_unit = VALUES(batch_size_unit),
                    time_per_batch_minutes = VALUES(time_per_batch_minutes),
                    finished_products_per_batch = VALUES(finished_products_per_batch),
                    output_per_batch = VALUES(output_per_batch),
                    output_per_batch_unit = VALUES(output_per_batch_unit),
                    manpower_required = VALUES(manpower_required),
                    machinery_required = VALUES(machinery_required),
                    special_requirements = VALUES(special_requirements)
                """,
                (
                    product_id,
                    data["batch_size"], data["batch_size_unit"], data["time_per_batch_minutes"],
                    data["finished_products_per_batch"], data["output_per_batch"], data["output_per_batch_unit"],
                    data["manpower_required"], data["machinery_required"], data["special_requirements"],
                ),
            )

    def raw_material_requirements(self, product_id: int, batch_size: float) -> list[dict]:
        """Per-batch material requirement, derived from the product's
        ACTIVE formula: quantity_per_unit x batch_size. Empty if the
        product has no active formula yet.
        """
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT fl.material_id, rm.name AS material_name, rm.unit, fl.quantity_per_unit
                FROM formulas f
                JOIN formula_lines fl ON fl.formula_id = f.id
                JOIN raw_materials rm ON rm.id = fl.material_id
                WHERE f.product_id = %s AND f.is_active = 1
                ORDER BY rm.name
                """,
                (product_id,),
            )
            rows = cur.fetchall()
        return [
            {
                "material_id": r["material_id"],
                "material_name": r["material_name"],
                "unit": r["unit"],
                "quantity_per_batch": float(r["quantity_per_unit"]) * batch_size,
            }
            for r in rows
        ]

    def has_active_formula(self, product_id: int) -> bool:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM formulas WHERE product_id = %s AND is_active = 1 LIMIT 1",
                (product_id,),
            )
            return cur.fetchone() is not None
