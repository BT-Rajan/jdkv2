from perennia_files import PerenniaFiles

from app.core.errors import AppError
from app.domain.attachments.repository import AttachmentRepository

VALID_ENTITY_TYPES = {"customer", "supplier", "product", "order"}


class AttachmentService:
    def __init__(self, repo: AttachmentRepository, files: PerenniaFiles):
        self._repo = repo
        self._files = files

    def upload(self, identity, entity_type: str, entity_id: str, filename: str,
               data: bytes, label: str | None) -> dict:
        if entity_type not in VALID_ENTITY_TYPES:
            raise AppError("validation_error")

        logical_file = self._files.upload(filename, data, identity=identity, created_by=identity.subject_id)
        attachment_id = self._repo.link(entity_type, entity_id, logical_file.id, filename, label, identity.subject_id)
        return self._repo.get(attachment_id)

    def list_for_entity(self, identity, entity_type: str, entity_id: str) -> list[dict]:
        return self._repo.list_for_entity(entity_type, entity_id)

    def download(self, identity, attachment_id: str):
        attachment = self._repo.get(attachment_id)
        if not attachment:
            raise AppError("not_found")
        version, data = self._files.download(attachment["file_id"], identity=identity)
        return attachment, version, data

    def delete(self, identity, attachment_id: str) -> None:
        attachment = self._repo.get(attachment_id)
        if not attachment:
            raise AppError("not_found")
        self._files.delete(attachment["file_id"], identity=identity, deleted_by=identity.subject_id)
        self._repo.unlink(attachment_id)
