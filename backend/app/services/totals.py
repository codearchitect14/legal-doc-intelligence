from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.case_totals import CaseTotals
from app.models.document import Document, ExtractedField


def _sum_field(case_id: UUID, field_name: str, db: Session) -> Decimal:
    values = db.execute(
        select(ExtractedField.field_value)
        .join(Document, ExtractedField.document_id == Document.id)
        .where(Document.case_id == case_id, ExtractedField.field_name == field_name)
    ).scalars().all()
    return sum((Decimal(value) for value in values), Decimal(0))


def compute_totals(case_id: UUID, db: Session) -> CaseTotals:
    total_billed = _sum_field(case_id, "billed_amount", db)
    total_wages = _sum_field(case_id, "wage_amount", db)

    totals = db.execute(
        select(CaseTotals).where(CaseTotals.case_id == case_id)
    ).scalar_one_or_none()

    if totals is None:
        totals = CaseTotals(case_id=case_id, total_billed=total_billed, total_wages=total_wages)
        db.add(totals)
    else:
        totals.total_billed = total_billed
        totals.total_wages = total_wages
        totals.computed_at = datetime.now(UTC)

    db.commit()
    db.refresh(totals)
    return totals
