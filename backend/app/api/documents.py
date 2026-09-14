import zipfile
from io import BytesIO
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.deps import get_current_firm_id
from app.models.case import Case
from app.models.document import Document
from app.schemas.document import DocumentOut
from app.services.storage import save_upload
from app.workers.document_processing import process_document

router = APIRouter(prefix="/cases/{case_id}/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}


def _get_owned_case(case_id: UUID, firm_id: UUID, db: Session) -> Case:
    case = db.execute(
        select(Case).where(Case.id == case_id, Case.firm_id == firm_id)
    ).scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


def _validate_size(content: bytes, filename: str) -> None:
    max_bytes = get_settings().max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"{filename} exceeds the {get_settings().max_upload_size_mb}MB upload limit",
        )


def _create_document(
    case: Case, filename: str, content: bytes, db: Session, background_tasks: BackgroundTasks
) -> Document:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {extension or filename}",
        )
    _validate_size(content, filename)

    document = Document(case_id=case.id, file_path="", ocr_status="pending")
    db.add(document)
    db.flush()

    document.file_path = save_upload(case.firm_id, case.id, document.id, filename, content)
    db.commit()
    db.refresh(document)

    background_tasks.add_task(process_document, document.id, db)
    return document


@router.post("", response_model=list[DocumentOut], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    case_id: UUID,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    firm_id: UUID = Depends(get_current_firm_id),
    db: Session = Depends(get_db),
) -> list[Document]:
    case = _get_owned_case(case_id, firm_id, db)
    created: list[Document] = []

    for upload in files:
        content = await upload.read()
        filename = upload.filename or f"upload-{uuid4()}"

        if Path(filename).suffix.lower() == ".zip":
            try:
                archive = zipfile.ZipFile(BytesIO(content))
            except zipfile.BadZipFile as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid archive: {filename}"
                ) from exc
            for member in archive.infolist():
                if member.is_dir():
                    continue
                member_name = Path(member.filename).name
                if not member_name or Path(member_name).suffix.lower() not in ALLOWED_EXTENSIONS:
                    continue
                member_content = archive.read(member)
                created.append(
                    _create_document(case, member_name, member_content, db, background_tasks)
                )
        else:
            created.append(_create_document(case, filename, content, db, background_tasks))

    if not created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No supported files found in upload"
        )
    return created


@router.get("", response_model=list[DocumentOut])
def list_documents(
    case_id: UUID, firm_id: UUID = Depends(get_current_firm_id), db: Session = Depends(get_db)
) -> list[Document]:
    _get_owned_case(case_id, firm_id, db)
    return list(db.execute(select(Document).where(Document.case_id == case_id)).scalars())


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    case_id: UUID,
    document_id: UUID,
    firm_id: UUID = Depends(get_current_firm_id),
    db: Session = Depends(get_db),
) -> Document:
    _get_owned_case(case_id, firm_id, db)
    document = db.execute(
        select(Document).where(Document.id == document_id, Document.case_id == case_id)
    ).scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
