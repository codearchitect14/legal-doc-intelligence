from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class TimelineEventOut(BaseModel):
    id: UUID
    case_id: UUID
    event_date: date
    description: str
    source_document_id: UUID

    model_config = {"from_attributes": True}


class CaseTotalsOut(BaseModel):
    case_id: UUID
    total_billed: Decimal
    total_wages: Decimal
    computed_at: datetime

    model_config = {"from_attributes": True}


class InconsistencyFlagOut(BaseModel):
    id: UUID
    case_id: UUID
    flag_type: str
    description: str
    related_document_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisResult(BaseModel):
    chronology: list[TimelineEventOut]
    totals: CaseTotalsOut
    inconsistencies: list[InconsistencyFlagOut]
