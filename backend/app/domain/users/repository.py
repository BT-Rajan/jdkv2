"""
User administration repository.

Reads join JDK's own `user_profiles` table with perennia-auth's
`auth_subjects` / `auth_identifiers` and perennia-access's `user_roles` /
`roles` tables directly - all three live in the same physical database (see
docs/06-architecture.md and perennia-reference-app's precedent of a shared
schema). This is read-only: perennia-auth and perennia-access remain the only
writers of their own tables. JDK writes only to `user_profiles` and
`user_admin_audit`, both of which JDK owns outright.

No public perennia-auth API lists/searches subjects (by design - it is an
authentication package, not a directory service), which is why this
read path exists rather than reimplementing it against a nonexistent
endpoint.
"""
import json
import uuid
from datetime import datetime, timezone

from app.core.database import Database


class UserAdminRepository:
    def __init__(self, db: Database):
        self._db = db

    # ------------------------------------------------------------- profile

    def upsert_profile(self, subject_id: str, full_name: str,
                        phone: str | None, department: str | None) -> None:
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO user_profiles (subject_id, full_name, phone, department)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    full_name = VALUES(full_name),
                    phone = VALUES(phone),
                    department = VALUES(department)
                """,
                (subject_id, full_name, phone, department),
            )

    def get_profile(self, subject_id: str) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT subject_id, full_name, phone, department, created_at "
                "FROM user_profiles WHERE subject_id = %s",
                (subject_id,),
            )
            return cur.fetchone()

    # ------------------------------------------------------------- search

    def search(self, keyword: str | None, status: str | None,
               role: str | None, limit: int, offset: int) -> tuple[list[dict], int]:
        clauses = []
        params: list = []

        if keyword:
            clauses.append(
                "(ai.email LIKE %s OR up.full_name LIKE %s OR up.phone LIKE %s)"
            )
            like = f"%{keyword}%"
            params.extend([like, like, like])
        if status:
            clauses.append("s.status = %s")
            params.append(status)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        role_join = ""
        if role:
            role_join = (
                "JOIN user_roles ur2 ON ur2.subject_id = s.id "
                "JOIN roles r2 ON r2.id = ur2.role_id AND r2.code = %s "
            )

        base_from = f"""
            FROM auth_subjects s
            JOIN auth_identifiers ai ON ai.subject_id = s.id
            LEFT JOIN user_profiles up ON up.subject_id = s.id
            {role_join}
            {where_sql}
        """
        count_params = ([role] if role else []) + params

        with self._db.cursor() as cur:
            cur.execute(f"SELECT COUNT(DISTINCT s.id) AS total {base_from}", count_params)
            total = cur.fetchone()["total"]

            cur.execute(
                f"""
                SELECT DISTINCT s.id AS subject_id, s.status, s.created_at,
                       ai.email, up.full_name, up.phone, up.department
                {base_from}
                ORDER BY s.created_at DESC
                LIMIT %s OFFSET %s
                """,
                count_params + [limit, offset],
            )
            rows = cur.fetchall()

        return rows, total

    def get_identifier(self, subject_id: str) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT s.id AS subject_id, s.status, s.created_at, ai.email "
                "FROM auth_subjects s "
                "JOIN auth_identifiers ai ON ai.subject_id = s.id "
                "WHERE s.id = %s",
                (subject_id,),
            )
            return cur.fetchone()

    # ------------------------------------------------------------- audit

    def record_audit(self, actor_subject_id: str, action: str, target_subject_id: str,
                      previous_state: dict | None, new_state: dict | None) -> None:
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO user_admin_audit
                    (id, actor_subject_id, action, target_subject_id, previous_state, new_state, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    actor_subject_id,
                    action,
                    target_subject_id,
                    json.dumps(previous_state) if previous_state is not None else None,
                    json.dumps(new_state) if new_state is not None else None,
                    datetime.now(timezone.utc),
                ),
            )

    def list_audit_for_target(self, target_subject_id: str) -> list[dict]:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT actor_subject_id, action, target_subject_id, "
                "previous_state, new_state, created_at "
                "FROM user_admin_audit WHERE target_subject_id = %s "
                "ORDER BY created_at DESC",
                (target_subject_id,),
            )
            rows = cur.fetchall()
            for row in rows:
                row["previous_state"] = json.loads(row["previous_state"]) if row["previous_state"] else None
                row["new_state"] = json.loads(row["new_state"]) if row["new_state"] else None
            return rows
