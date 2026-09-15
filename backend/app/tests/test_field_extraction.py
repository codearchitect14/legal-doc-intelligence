from decimal import Decimal
from uuid import uuid4

from app.models.document import Document
from app.services.field_extraction import extract_fields


def _make_document(category: str) -> Document:
    return Document(id=uuid4(), case_id=uuid4(), file_path="x.pdf", category=category)


def test_ner_friendly_date_is_extracted():
    document = _make_document("correspondence")
    fields = extract_fields(document, "This letter is dated January 5, 2024 and concerns the matter.")
    dates = [f for f in fields if f.field_name == "date"]
    assert any(f.field_date is not None and f.field_date.isoformat() == "2024-01-05" for f in dates)


def test_regex_only_numeric_date_is_extracted():
    document = _make_document("correspondence")
    fields = extract_fields(document, "Reference letter 01/05/2024 regarding the account.")
    dates = [f for f in fields if f.field_name == "date"]
    assert any(f.field_date is not None for f in dates)


def test_implausible_date_is_dropped():
    document = _make_document("correspondence")
    fields = extract_fields(document, "See the filing from 1750-01-01 for historical context.")
    dates = [f for f in fields if f.field_name == "date"]
    assert not any(f.field_date is not None and f.field_date.year < 1990 for f in dates)


def test_bare_year_citation_is_dropped_not_fabricated():
    document = _make_document("filing")
    fields = extract_fields(
        document,
        "The court's ruling in 1990 established the standard later applied in 2005.",
    )
    dates = [f for f in fields if f.field_name == "date"]
    # A bare year has no real day/month - accepting it would silently
    # invent a specific date (e.g. today's month/day) that was never in the
    # source text, which is worse than dropping it.
    assert not any(f.field_value in ("1990", "2005") for f in dates)


def test_amount_is_parsed_to_decimal_string():
    document = _make_document("bill")
    fields = extract_fields(document, "Invoice total: $1,234.56 due upon receipt.")
    amounts = [f for f in fields if f.field_name == "billed_amount"]
    assert any(f.field_value == "1234.56" for f in amounts)


def test_amount_only_extracted_for_bill_and_wage_categories():
    document = _make_document("correspondence")
    fields = extract_fields(document, "The amount mentioned, $1,234.56, is not a bill.")
    assert not any(f.field_name in ("billed_amount", "wage_amount") for f in fields)


def test_multiline_amount_span_is_dropped_not_concatenated():
    # A real itemized bill (a table with one $ figure per row) can produce a
    # spaCy MONEY entity that spans multiple table cells and newlines, e.g.
    # "$900 \n$1,225 \n$". Stripping non-digit characters from that would
    # silently concatenate it into $9,001,225 - a fabricated number nearly
    # 10,000x too large - instead of being rejected as unparseable.
    document = _make_document("bill")
    fields = extract_fields(
        document,
        "Total from Dr. Miller\n$900 \n$1,225 \n$325 higher\nItem 1 $300 Item 2 $350",
    )
    amounts = [f for f in fields if f.field_name == "billed_amount"]
    assert not any(f.field_value == "9001225" for f in amounts)
    assert all(Decimal(f.field_value) < Decimal(1_000_000) for f in amounts)
