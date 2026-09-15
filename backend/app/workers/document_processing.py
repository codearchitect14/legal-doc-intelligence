import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.embedding_chunk import EmbeddingChunk
from app.services.classification import chunk_and_embed, classify
from app.services.field_extraction import extract_fields
from app.services.text_extraction import extract_text

logger = logging.getLogger(__name__)


def process_document(document_id: UUID, db: Session) -> None:
    """Extract text, classify, and embed a document. Runs as a FastAPI
    BackgroundTask sharing the request's DB session (see Phase 2 plan)."""
    document = db.get(Document, document_id)
    if document is None:
        logger.error("document not found for processing", extra={"document_id": str(document_id)})
        return

    try:
        text, ocr_status = extract_text(document.file_path)
        document.ocr_status = ocr_status

        category, confidence = classify(text)
        document.category = category

        for field in extract_fields(document, text):
            db.add(field)

        for chunk_text, embedding in chunk_and_embed(text):
            db.add(
                EmbeddingChunk(
                    document_id=document.id,
                    chunk_text=chunk_text,
                    embedding=embedding,
                )
            )

        db.commit()
        logger.info(
            "document processed",
            extra={
                "document_id": str(document_id),
                "case_id": str(document.case_id),
                "category": category,
                "classification_confidence": confidence,
                "ocr_status": ocr_status,
            },
        )
    except Exception:
        logger.exception(
            "document processing failed", extra={"document_id": str(document_id)}
        )
        document.ocr_status = "failed"
        db.commit()
