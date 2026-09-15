import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation

import spacy
from dateutil import parser as dateutil_parser

from app.models.document import Document, ExtractedField

_nlp = None

# Sanity window for parsed dates: legal/medical case documents older than
# this are implausible for an active case, and dates far in the future are
# almost always a parsing artifact rather than a real document date.
MIN_PLAUSIBLE_DATE = date(1990, 1, 1)
MAX_FUTURE_SLACK = timedelta(days=365 * 2)

DATE_REGEX_PATTERNS = [
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",  # MM/DD/YYYY
    r"\b\d{1,2}-\d{1,2}-\d{2,4}\b",  # DD-MM-YYYY
    r"\b\d{4}-\d{2}-\d{2}\b",  # ISO YYYY-MM-DD
    (
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|"
        r"December)\s+\d{1,2},?\s+\d{4}\b"
    ),  # Month DD, YYYY
]
AMOUNT_REGEX_PATTERNS = [
    r"\$\s?[\d,]+(?:\.\d{2})?",  # $1,234.56
    r"\bUSD\s?[\d,]+(?:\.\d{2})?\b",  # USD 1,234.56
]


@dataclass
class _Candidate:
    start: int
    end: int
    text: str
    kind: str  # "date" or "amount"


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _merge_overlapping(candidates: list[_Candidate]) -> list[_Candidate]:
    """Collapse candidates whose character spans overlap, keeping the first
    (earliest-found) span so the same mention isn't extracted twice."""
    candidates = sorted(candidates, key=lambda c: c.start)
    merged: list[_Candidate] = []
    for candidate in candidates:
        if merged and candidate.start < merged[-1].end:
            continue
        merged.append(candidate)
    return merged


def _regex_candidates(text: str, patterns: list[str], kind: str) -> list[_Candidate]:
    candidates = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            candidates.append(_Candidate(match.start(), match.end(), match.group(), kind))
    return candidates


def _parse_valid_date(text: str, today: date) -> date | None:
    # dateutil silently fills in any day/month/year missing from the source
    # text using its `default` argument's value - so a bare year like "1990"
    # (extremely common in legal text as a citation year, e.g. "...in 1990,
    # the agency...") parses "successfully" into a specific day that was
    # never actually in the document. Parsing twice against two different
    # defaults and rejecting anything that disagrees is the standard way to
    # catch this: a fully-specified date agrees regardless of default, an
    # incomplete one doesn't.
    probe_a = datetime(1, 1, 1, tzinfo=UTC)
    probe_b = datetime(2, 2, 2, tzinfo=UTC)
    try:
        parsed_a = dateutil_parser.parse(text, fuzzy=False, default=probe_a)
        parsed_b = dateutil_parser.parse(text, fuzzy=False, default=probe_b)
    except (ValueError, OverflowError):
        return None
    if parsed_a != parsed_b:
        return None
    parsed = parsed_a.date()
    if parsed < MIN_PLAUSIBLE_DATE or parsed > today + MAX_FUTURE_SLACK:
        return None
    return parsed


def _parse_valid_amount(text: str) -> Decimal | None:
    normalized = re.sub(r"[^\d.]", "", text)
    if not normalized:
        return None
    try:
        value = Decimal(normalized)
    except InvalidOperation:
        return None
    if value <= 0:
        return None
    return value


def extract_fields(document: Document, text: str) -> list[ExtractedField]:
    """Extract validated dates/amounts/names from a document's text.

    Combines spaCy NER with a regex pass (regex catches formats the NER
    model misses, especially after imperfect OCR) and validates every
    candidate with dateutil/Decimal parsing plus sanity-range checks before
    it becomes an ExtractedField. Bad candidates are dropped, not stored.
    """
    fields: list[ExtractedField] = []
    if not text.strip():
        return fields

    doc = _get_nlp()(text)
    today = datetime.now(UTC).date()

    date_candidates = [
        _Candidate(ent.start_char, ent.end_char, ent.text, "date")
        for ent in doc.ents
        if ent.label_ == "DATE"
    ]
    date_candidates += _regex_candidates(text, DATE_REGEX_PATTERNS, "date")

    amount_candidates = [
        _Candidate(ent.start_char, ent.end_char, ent.text, "amount")
        for ent in doc.ents
        if ent.label_ == "MONEY"
    ]
    amount_candidates += _regex_candidates(text, AMOUNT_REGEX_PATTERNS, "amount")

    for candidate in _merge_overlapping(date_candidates):
        parsed = _parse_valid_date(candidate.text, today)
        if parsed is None:
            continue
        fields.append(
            ExtractedField(
                document_id=document.id,
                field_name="date",
                field_value=candidate.text,
                field_date=parsed,
            )
        )

    amount_field_name = {
        "bill": "billed_amount",
        "wage_record": "wage_amount",
    }.get(document.category)
    if amount_field_name:
        for candidate in _merge_overlapping(amount_candidates):
            parsed = _parse_valid_amount(candidate.text)
            if parsed is None:
                continue
            fields.append(
                ExtractedField(
                    document_id=document.id,
                    field_name=amount_field_name,
                    field_value=str(parsed),
                    field_date=None,
                )
            )

    if document.category == "medical_record":
        for ent in doc.ents:
            if ent.label_ == "ORG":
                fields.append(
                    ExtractedField(
                        document_id=document.id,
                        field_name="provider_name",
                        field_value=ent.text,
                        field_date=None,
                    )
                )
    elif document.category == "contract":
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PERSON"):
                fields.append(
                    ExtractedField(
                        document_id=document.id,
                        field_name="party",
                        field_value=ent.text,
                        field_date=None,
                    )
                )

    return fields
