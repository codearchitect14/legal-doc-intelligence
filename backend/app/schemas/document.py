from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: UUID
    case_id: UUID
    filename: str
    category: str | None
    ocr_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ExtractedFieldOut(BaseModel):
    id: UUID
    document_id: UUID
    field_name: str
    field_value: str
    field_date: date | None

    model_config = {"from_attributes": True}
