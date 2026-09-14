from uuid import UUID

from pydantic import BaseModel


class CaseCreateRequest(BaseModel):
    title: str


class CaseOut(BaseModel):
    id: UUID
    firm_id: UUID
    title: str
    status: str

    model_config = {"from_attributes": True}
