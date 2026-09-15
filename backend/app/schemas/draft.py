from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.services.draft import OUTPUT_TYPES


class DraftRequest(BaseModel):
    output_type: str

    @field_validator("output_type")
    @classmethod
    def validate_output_type(cls, value: str) -> str:
        if value not in OUTPUT_TYPES:
            raise ValueError(f"output_type must be one of {OUTPUT_TYPES}")
        return value


class DraftUpdateRequest(BaseModel):
    content: str


class DraftOutputOut(BaseModel):
    id: UUID
    case_id: UUID
    output_type: str
    content: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
