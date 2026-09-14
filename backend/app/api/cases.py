from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_firm_id
from app.models.case import Case
from app.schemas.case import CaseCreateRequest, CaseOut

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseCreateRequest,
    firm_id: UUID = Depends(get_current_firm_id),
    db: Session = Depends(get_db),
) -> Case:
    case = Case(firm_id=firm_id, title=payload.title)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("", response_model=list[CaseOut])
def list_cases(
    firm_id: UUID = Depends(get_current_firm_id), db: Session = Depends(get_db)
) -> list[Case]:
    return list(db.execute(select(Case).where(Case.firm_id == firm_id)).scalars())


@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: UUID,
    firm_id: UUID = Depends(get_current_firm_id),
    db: Session = Depends(get_db),
) -> Case:
    case = db.execute(
        select(Case).where(Case.id == case_id, Case.firm_id == firm_id)
    ).scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case
