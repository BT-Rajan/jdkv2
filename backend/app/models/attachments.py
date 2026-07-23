from datetime import datetime
from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    file_id: str
    filename: str
    label: str | None
    uploaded_by_subject_id: str | None
    created_at: datetime
