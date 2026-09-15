from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_firm_id
from app.models.case import Case
from app.models.draft_output import DraftOutput
from app.schemas.draft import DraftOutputOut, DraftRequest, DraftUpdateRequest
from app.services.draft import export_docx, generate_draft, update_draft_content

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


def _get_owned_draft(case_id: UUID, draft_id: UUID, firm_id: UUID, db: Session) -> DraftOutput:
    _get_owned_case(case_id, firm_id, db)
    draft = db.execute(
        select(DraftOutput).where(DraftOutput.id == draft_id, DraftOutput.case_id == case_id)
    ).scalar_one_or_none()
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    return draft


@router.get("/drafts/{draft_id}", response_model=DraftOutputOut)
def get_draft(
    case_id: UUID,
    draft_id: UUID,
    firm_id: UUID = Depends(get_current_firm_id),
    db: Session = Depends(get_db),
) -> DraftOutput:
    return _get_owned_draft(case_id, draft_id, firm_id, db)


@router.patch("/drafts/{draft_id}", response_model=DraftOutputOut)
def edit_draft(
    case_id: UUID,
    draft_id: UUID,
    payload: DraftUpdateRequest,
    firm_id: UUID = Depends(get_current_firm_id),
    db: Session = Depends(get_db),
) -> DraftOutput:
    draft = _get_owned_draft(case_id, draft_id, firm_id, db)
    return update_draft_content(draft, payload.content, db)


@router.get("/drafts/{draft_id}/export")
def export_draft(
    case_id: UUID,
    draft_id: UUID,
    firm_id: UUID = Depends(get_current_firm_id),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    case = _get_owned_case(case_id, firm_id, db)
    draft = _get_owned_draft(case_id, draft_id, firm_id, db)
    content = export_docx(draft, case)
    filename = f"{draft.output_type}-{draft.id}.docx"
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
