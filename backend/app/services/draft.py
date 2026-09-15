from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm.llm_router import generate_narrative
from app.models.case import Case
from app.models.case_totals import CaseTotals
from app.models.draft_output import DraftOutput
from app.models.inconsistency_flag import InconsistencyFlag
from app.models.timeline_event import TimelineEvent

OUTPUT_TYPES = ("chronology_summary", "demand_letter")


def narrative_required(output_type: str, inconsistencies: list[InconsistencyFlag]) -> bool:
    """Combined type + content decision (Section 5's "is narrative reasoning
    required" branch): a demand letter always needs persuasive connecting
    narrative (Section 6 item 6); a plain chronology summary only escalates
    to the LLM when there's something worth explaining in prose."""
    if output_type == "demand_letter":
        return True
    if output_type == "chronology_summary":
        return len(inconsistencies) > 0
    raise ValueError(f"Unknown output_type: {output_type}")


def _format_chronology(chronology: list[TimelineEvent]) -> str:
    if not chronology:
        return "No dated events were extracted for this case."
    return "\n".join(f"- {e.event_date.isoformat()}: {e.description}" for e in chronology)


def _format_inconsistencies(inconsistencies: list[InconsistencyFlag]) -> str:
    if not inconsistencies:
        return "No inconsistencies were flagged."
    return "\n".join(f"- [{f.flag_type}] {f.description}" for f in inconsistencies)


def build_prompt(
    case: Case,
    chronology: list[TimelineEvent],
    totals: CaseTotals | None,
    inconsistencies: list[InconsistencyFlag],
    output_type: str,
) -> str:
    """The single consolidated prompt (Section 10.3): chronology, totals,
    and flagged issues condensed into one structured block. Never raw
    document text — that is exactly what keeps the per-case token cost low."""
    total_billed = totals.total_billed if totals else 0
    total_wages = totals.total_wages if totals else 0
    task = (
        "Write a persuasive demand letter"
        if output_type == "demand_letter"
        else "Write a plain-language case summary"
    )
    return (
        f"{task} for the case titled \"{case.title}\".\n\n"
        f"Case chronology:\n{_format_chronology(chronology)}\n\n"
        f"Totals: billed ${total_billed}, wage loss ${total_wages}\n\n"
        f"Flagged inconsistencies:\n{_format_inconsistencies(inconsistencies)}\n\n"
        "Write only the connecting narrative language; do not invent facts, "
        "dates, or amounts beyond what is listed above."
    )


def assemble_template(
    case: Case,
    chronology: list[TimelineEvent],
    totals: CaseTotals | None,
    inconsistencies: list[InconsistencyFlag],
    output_type: str,
) -> str:
    """Deterministic, zero-token draft. Used directly for a chronology
    summary with nothing to explain, and as the guaranteed fallback if the
    LLM router returns None (Section 10.1: never leave a case without
    output)."""
    total_billed = totals.total_billed if totals else 0
    total_wages = totals.total_wages if totals else 0
    heading = "DEMAND LETTER" if output_type == "demand_letter" else "CASE SUMMARY"
    return (
        f"{heading}\n"
        f"Case: {case.title}\n\n"
        f"Chronology:\n{_format_chronology(chronology)}\n\n"
        f"Total billed: ${total_billed}\n"
        f"Total wage loss: ${total_wages}\n\n"
        f"Inconsistencies:\n{_format_inconsistencies(inconsistencies)}\n"
    )


def generate_draft(case_id: UUID, output_type: str, db: Session) -> DraftOutput:
    if output_type not in OUTPUT_TYPES:
        raise ValueError(f"Unknown output_type: {output_type}")

    case = db.get(Case, case_id)
    chronology = list(
        db.execute(
            select(TimelineEvent)
            .where(TimelineEvent.case_id == case_id)
            .order_by(TimelineEvent.event_date)
        ).scalars()
    )
    totals = db.execute(
        select(CaseTotals).where(CaseTotals.case_id == case_id)
    ).scalar_one_or_none()
    inconsistencies = list(
        db.execute(
            select(InconsistencyFlag).where(InconsistencyFlag.case_id == case_id)
        ).scalars()
    )

    status = "template_fallback"
    if narrative_required(output_type, inconsistencies):
        prompt = build_prompt(case, chronology, totals, inconsistencies, output_type)
        narrative = generate_narrative(prompt, case_id, db)
        if narrative is not None:
            content = narrative
            status = "complete"
        else:
            content = assemble_template(case, chronology, totals, inconsistencies, output_type)
    else:
        content = assemble_template(case, chronology, totals, inconsistencies, output_type)
        status = "complete"

    draft = DraftOutput(case_id=case_id, output_type=output_type, content=content, status=status)
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft
