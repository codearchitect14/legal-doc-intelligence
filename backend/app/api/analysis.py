from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_firm_id
from app.models.case import Case
from app.models.inconsistency_flag import InconsistencyFlag
from app.models.timeline_event import TimelineEvent
from app.schemas.analysis import (
    AnalysisResult,
    CaseTotalsOut,
    InconsistencyFlagOut,
    TimelineEventOut,
)
from app.services.chronology import build_chronology
from app.services.inconsistency import detect_inconsistencies
from app.services.totals import compute_totals

router = APIRouter(prefix="/cases/{case_id}", tags=["analysis"])


def _get_owned_case(case_id: UUID, firm_id: UUID, db: Session) -> Case:
    case = db.execute(
        select(Case).where(Case.id == case_id, Case.firm_id == firm_id)
    ).scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.post("/analyze", response_model=AnalysisResult)
def analyze_case(
    case_id: UUID, firm_id: UUID = Depends(get_current_firm_id), db: Session = Depends(get_db)
) -> AnalysisResult:
    _get_owned_case(case_id, firm_id, db)
    chronology = build_chronology(case_id, db)
    totals = compute_totals(case_id, db)
    inconsistencies = detect_inconsistencies(case_id, db)
    return AnalysisResult(
        chronology=[TimelineEventOut.model_validate(e) for e in chronology],
        totals=CaseTotalsOut.model_validate(totals),
        inconsistencies=[InconsistencyFlagOut.model_validate(f) for f in inconsistencies],
    )


@router.get("/chronology", response_model=list[TimelineEventOut])
def get_chronology(
    case_id: UUID, firm_id: UUID = Depends(get_current_firm_id), db: Session = Depends(get_db)
) -> list[TimelineEvent]:
    _get_owned_case(case_id, firm_id, db)
    events = list(
        db.execute(
            select(TimelineEvent)
            .where(TimelineEvent.case_id == case_id)
            .order_by(TimelineEvent.event_date)
        ).scalars()
    )
    return events


@router.get("/totals", response_model=CaseTotalsOut)
def get_totals(
    case_id: UUID, firm_id: UUID = Depends(get_current_firm_id), db: Session = Depends(get_db)
) -> CaseTotalsOut:
    case = _get_owned_case(case_id, firm_id, db)
    if case.totals is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Totals have not been computed yet; call POST /analyze first",
        )
    return CaseTotalsOut.model_validate(case.totals)


@router.get("/inconsistencies", response_model=list[InconsistencyFlagOut])
def get_inconsistencies(
    case_id: UUID, firm_id: UUID = Depends(get_current_firm_id), db: Session = Depends(get_db)
) -> list[InconsistencyFlag]:
    _get_owned_case(case_id, firm_id, db)
    return list(
        db.execute(
            select(InconsistencyFlag).where(InconsistencyFlag.case_id == case_id)
        ).scalars()
    )
