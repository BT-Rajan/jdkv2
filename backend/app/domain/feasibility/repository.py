import json
import uuid

from app.core.database import Database

OUTCOMES_ALLOWING_QUOTATION = ("feasible", "partially_feasible", "feasible_on_later_date")


class FeasibilityRepository:
    """History table only: no update() for business fields and no delete().

    The single amend() path is reserved for administrators correcting a
    finalized record (see app/api/feasibility.py) - everything else about a
    feasibility run is fixed at creation time.
    """

    def __init__(self, db: Database):
        self._db = db

    def create(self, customer_id: int, product_id: int, quantity_kg: float,
               requested_delivery_date, outcome: str, estimated_fulfillment_date,
               promptly_available_kg: float, remaining_kg: float, constraints: list[dict],
               notes: str | None, created_by_subject_id: str) -> str:
        run_id = str(uuid.uuid4())
        chain_id = run_id  # this run originates the chain
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO feasibility_runs
                    (id, chain_id, customer_id, product_id, quantity_kg, requested_delivery_date,
                     outcome, estimated_fulfillment_date, promptly_available_kg, remaining_kg,
                     constraints_json, status, notes, created_by_subject_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'open',%s,%s)
                """,
                (run_id, chain_id, customer_id, product_id, quantity_kg, requested_delivery_date,
                 outcome, estimated_fulfillment_date, promptly_available_kg, remaining_kg,
                 json.dumps(constraints), notes, created_by_subject_id),
            )
        return run_id

    def get(self, run_id: str) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT fr.*, c.name AS customer_name, p.name AS product_name
                FROM feasibility_runs fr
                JOIN customers c ON c.id = fr.customer_id
                JOIN products p ON p.id = fr.product_id
                WHERE fr.id = %s
                """,
                (run_id,),
            )
            row = cur.fetchone()
            if row and row.get("constraints_json"):
                row["constraints"] = json.loads(row["constraints_json"])
            elif row:
                row["constraints"] = []
            return row

    def search(self, customer_id: int | None, outcome: str | None, status: str | None,
               limit: int, offset: int) -> tuple[list[dict], int]:
        clauses, params = [], []
        if customer_id:
            clauses.append("fr.customer_id = %s")
            params.append(customer_id)
        if outcome:
            clauses.append("fr.outcome = %s")
            params.append(outcome)
        if status:
            clauses.append("fr.status = %s")
            params.append(status)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        base = f"""
            FROM feasibility_runs fr
            JOIN customers c ON c.id = fr.customer_id
            JOIN products p ON p.id = fr.product_id
            {where_sql}
        """
        with self._db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total {base}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"""
                SELECT fr.*, c.name AS customer_name, p.name AS product_name
                {base}
                ORDER BY fr.created_at DESC
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = cur.fetchall()
            for row in rows:
                row["constraints"] = json.loads(row["constraints_json"]) if row.get("constraints_json") else []
            return rows, total

    def mark_converted(self, run_id: str) -> None:
        with self._db.transaction() as cur:
            cur.execute("UPDATE feasibility_runs SET status = 'converted' WHERE id = %s", (run_id,))

    def amend_notes(self, run_id: str, notes: str | None, amended_by_subject_id: str) -> None:
        with self._db.transaction() as cur:
            cur.execute(
                "UPDATE feasibility_runs SET notes = %s, amended_at = NOW(), amended_by_subject_id = %s WHERE id = %s",
                (notes, amended_by_subject_id, run_id),
            )
