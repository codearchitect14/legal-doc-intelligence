from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from itertools import pairwise
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document import Document, ExtractedField
from app.models.inconsistency_flag import InconsistencyFlag

# Gap threshold for flagging a possible missing follow-up medical record.
MISSING_FOLLOWUP_GAP_DAYS = 60


def _conflicting_amounts_on_same_date(case_id: UUID, db: Session) -> list[InconsistencyFlag]:
    """A billed_amount field never carries its own field_date (only
    field_name="date" fields do) — an amount's date is whatever date(s)
    were extracted from the *same document*, so this correlates the two
    by document rather than by ExtractedField.field_date directly."""
    rows = db.execute(
        select(ExtractedField, Document)
        .join(Document, ExtractedField.document_id == Document.id)
        .where(
            Document.case_id == case_id,
            ExtractedField.field_name.in_(("billed_amount", "date")),
        )
    ).all()

    dates_by_document: dict = defaultdict(list)
    amounts_by_document: dict = defaultdict(list)
    for field, document in rows:
        if field.field_name == "date" and field.field_date is not None:
            dates_by_document[document.id].append(field.field_date)
        elif field.field_name == "billed_amount":
            amounts_by_document[document.id].append(Decimal(field.field_value))

    by_date: dict = defaultdict(list)
    for document_id, amounts in amounts_by_document.items():
        for event_date in dates_by_document.get(document_id, []):
            for amount in amounts:
                by_date[event_date].append((amount, document_id))

    flags = []
    for event_date, entries in by_date.items():
        distinct_amounts = {amount for amount, _ in entries}
        if len(distinct_amounts) > 1:
            flags.append(
                InconsistencyFlag(
                    case_id=case_id,
                    flag_type="conflicting_amounts_same_date",
                    description=(
                        f"Multiple billed amounts reported for {event_date.isoformat()}: "
                        f"{', '.join(str(a) for a in sorted(distinct_amounts))}"
                    ),
                    related_document_id=entries[0][1],
                )
            )
    return flags


def _possible_missing_followup(case_id: UUID, db: Session) -> list[InconsistencyFlag]:
    rows = db.execute(
        select(ExtractedField, Document)
        .join(Document, ExtractedField.document_id == Document.id)
        .where(
            Document.case_id == case_id,
            Document.category == "medical_record",
            ExtractedField.field_name == "date",
        )
    ).all()

    dated_documents = sorted(
        {(field.field_date, document.id) for field, document in rows if field.field_date},
        key=lambda pair: pair[0],
    )

    flags = []
    for (earlier_date, earlier_doc_id), (later_date, _) in pairwise(dated_documents):
        if later_date - earlier_date > timedelta(days=MISSING_FOLLOWUP_GAP_DAYS):
            flags.append(
                InconsistencyFlag(
                    case_id=case_id,
                    flag_type="possible_missing_followup",
                    description=(
                        f"Gap of {(later_date - earlier_date).days} days between medical "
                        f"records dated {earlier_date.isoformat()} and {later_date.isoformat()}"
                    ),
                    related_document_id=earlier_doc_id,
                )
            )
    return flags


def detect_inconsistencies(case_id: UUID, db: Session) -> list[InconsistencyFlag]:
    db.execute(delete(InconsistencyFlag).where(InconsistencyFlag.case_id == case_id))

    flags = _conflicting_amounts_on_same_date(case_id, db) + _possible_missing_followup(
        case_id, db
    )
    for flag in flags:
        db.add(flag)

    db.commit()
    return flags
