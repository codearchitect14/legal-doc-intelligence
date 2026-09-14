import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.embedding_chunk import EmbeddingChunk
from app.services.classification import chunk_and_embed, classify
from app.services.text_extraction import extract_text

logger = logging.getLogger(__name__)


def process_document(document_id: UUID, db: Session) -> None:
    """Extract text, classify, and embed a document. Runs as a FastAPI
    BackgroundTask sharing the request's DB session (see Phase 2 plan)."""
    document = db.get(Document, document_id)
    if document is None:
        logger.error("process_document: document %s not found", document_id)
        return

    try:
        text, ocr_status = extract_text(document.file_path)
        document.ocr_status = ocr_status

        category, _confidence = classify(text)
        document.category = category

        for chunk_text, embedding in chunk_and_embed(text):
            db.add(
                EmbeddingChunk(
                    document_id=document.id,
                    chunk_text=chunk_text,
                    embedding=embedding,
                )
            )

        db.commit()
    except Exception:
        logger.exception("process_document failed for document %s", document_id)
        document.ocr_status = "failed"
        db.commit()
