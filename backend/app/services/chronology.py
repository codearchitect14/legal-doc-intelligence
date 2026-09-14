from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document import Document, ExtractedField
from app.models.timeline_event import TimelineEvent


def build_chronology(case_id: UUID, db: Session) -> list[TimelineEvent]:
    """Recompute the case's timeline from scratch: delete any existing
    TimelineEvent rows for this case, then rebuild from every "date"
    ExtractedField across the case's documents."""
    db.execute(delete(TimelineEvent).where(TimelineEvent.case_id == case_id))

    date_fields = db.execute(
        select(ExtractedField, Document)
        .join(Document, ExtractedField.document_id == Document.id)
        .where(Document.case_id == case_id, ExtractedField.field_name == "date")
    ).all()

    events = []
    for field, document in date_fields:
        category_label = (document.category or "document").replace("_", " ")
        event = TimelineEvent(
            case_id=case_id,
            event_date=field.field_date,
            description=f"{category_label}: {field.field_value}",
            source_document_id=document.id,
        )
        db.add(event)
        events.append(event)

    db.commit()
    events.sort(key=lambda e: e.event_date)
    return events
