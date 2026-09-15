from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_firm_id
from app.models.case import Case
from app.models.draft_output import DraftOutput
from app.schemas.draft import DraftOutputOut, DraftRequest
from app.services.draft import generate_draft

router = APIRouter(prefix="/cases/{case_id}", tags=["draft"])


def _get_owned_case(case_id: UUID, firm_id: UUID, db: Session) -> Case:
    case = db.execute(
        select(Case).where(Case.id == case_id, Case.firm_id == firm_id)
    ).scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.post("/draft", response_model=DraftOutputOut, status_code=status.HTTP_201_CREATED)
def create_draft(
    case_id: UUID,
    payload: DraftRequest,
    firm_id: UUID = Depends(get_current_firm_id),
    db: Session = Depends(get_db),
) -> DraftOutput:
    case = _get_owned_case(case_id, firm_id, db)
    if case.totals is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case has not been analyzed yet; call POST /analyze first",
        )
    return generate_draft(case_id, payload.output_type, db)


@router.get("/drafts", response_model=list[DraftOutputOut])
def list_drafts(
    case_id: UUID, firm_id: UUID = Depends(get_current_firm_id), db: Session = Depends(get_db)
) -> list[DraftOutput]:
    _get_owned_case(case_id, firm_id, db)
    return list(
        db.execute(select(DraftOutput).where(DraftOutput.case_id == case_id)).scalars()
    )


@router.get("/drafts/{draft_id}", response_model=DraftOutputOut)
def get_draft(
    case_id: UUID,
    draft_id: UUID,
    firm_id: UUID = Depends(get_current_firm_id),
    db: Session = Depends(get_db),
) -> DraftOutput:
    _get_owned_case(case_id, firm_id, db)
    draft = db.execute(
        select(DraftOutput).where(DraftOutput.id == draft_id, DraftOutput.case_id == case_id)
    ).scalar_one_or_none()
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    return draft
