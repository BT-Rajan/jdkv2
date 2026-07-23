import uuid

from app.core.database import Database


class AttachmentRepository:
    def __init__(self, db: Database):
        self._db = db

    def link(self, entity_type: str, entity_id: str, file_id: str, filename: str,
              label: str | None, uploaded_by_subject_id: str) -> str:
        attachment_id = str(uuid.uuid4())
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO entity_attachments
                    (id, entity_type, entity_id, file_id, filename, label, uploaded_by_subject_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (attachment_id, entity_type, entity_id, file_id, filename, label, uploaded_by_subject_id),
            )
        return attachment_id

    def list_for_entity(self, entity_type: str, entity_id: str) -> list[dict]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT id, entity_type, entity_id, file_id, filename, label, uploaded_by_subject_id, created_at
                FROM entity_attachments
                WHERE entity_type = %s AND entity_id = %s
                ORDER BY created_at DESC
                """,
                (entity_type, entity_id),
            )
            return cur.fetchall()

    def get(self, attachment_id: str) -> dict | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM entity_attachments WHERE id = %s", (attachment_id,))
            return cur.fetchone()

    def unlink(self, attachment_id: str) -> None:
        with self._db.transaction() as cur:
            cur.execute("DELETE FROM entity_attachments WHERE id = %s", (attachment_id,))
