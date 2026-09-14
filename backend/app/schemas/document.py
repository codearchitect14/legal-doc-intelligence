from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: UUID
    case_id: UUID
    category: str | None
    ocr_status: str
    created_at: datetime

    model_config = {"from_attributes": True}
