import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.common import CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.document import Document

# Dimension matches the sentence-transformers all-MiniLM-L6-v2 embedding model
# chosen in PROJECT_PLAN_v2.md Section 7. Update if the embedding model changes.
EMBEDDING_DIM = 384


class EmbeddingChunk(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "embedding_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)

    document: Mapped["Document"] = relationship(back_populates="embedding_chunks")
