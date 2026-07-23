from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import Response

from perennia_access import AuthenticatedIdentity

from app.core.security import require_permission, files as files_client
from app.core.database import Database
from app.core.config import load_settings
from app.domain.attachments.repository import AttachmentRepository
from app.domain.attachments.service import AttachmentService
from app.permissions.definitions import FILE_UPLOAD, FILE_VIEW, FILE_DELETE
from app.models.attachments import AttachmentResponse

router = APIRouter(prefix="/api/attachments", tags=["attachments"])

_db = Database(load_settings())
_service = AttachmentService(AttachmentRepository(_db), files_client)


@router.get("", response_model=list[AttachmentResponse])
def list_attachments(entity_type: str, entity_id: str,
                      identity: AuthenticatedIdentity = Depends(require_permission(FILE_VIEW))):
    return [AttachmentResponse(**row) for row in _service.list_for_entity(identity, entity_type, entity_id)]


@router.post("", response_model=AttachmentResponse)
async def upload_attachment(
    entity_type: str = Form(...),
    entity_id: str = Form(...),
    label: str | None = Form(None),
    file: UploadFile = File(...),
    identity: AuthenticatedIdentity = Depends(require_permission(FILE_UPLOAD)),
):
    data = await file.read()
    result = _service.upload(identity, entity_type, entity_id, file.filename, data, label)
    return AttachmentResponse(**result)


@router.get("/{attachment_id}/download")
def download_attachment(attachment_id: str,
                         identity: AuthenticatedIdentity = Depends(require_permission(FILE_VIEW))):
    attachment, version, data = _service.download(identity, attachment_id)
    return Response(
        content=data,
        media_type=version.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{attachment["filename"]}"'},
    )


@router.delete("/{attachment_id}")
def delete_attachment(attachment_id: str,
                       identity: AuthenticatedIdentity = Depends(require_permission(FILE_DELETE))):
    _service.delete(identity, attachment_id)
    return {"status": "deleted"}
