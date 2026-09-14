import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.common import CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.embedding_chunk import EmbeddingChunk


class Document(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "documents"

    case_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ocr_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

    case: Mapped["Case"] = relationship(back_populates="documents")
    extracted_fields: Mapped[list["ExtractedField"]] = relationship(back_populates="document")
    embedding_chunks: Mapped[list["EmbeddingChunk"]] = relationship(back_populates="document")


class ExtractedField(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "extracted_fields"

    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    field_value: Mapped[str] = mapped_column(Text, nullable=False)
    field_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    document: Mapped["Document"] = relationship(back_populates="extracted_fields")
