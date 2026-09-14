import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.common import CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.draft_output import DraftOutput
    from app.models.firm import Firm
    from app.models.model_usage_log import ModelUsageLog
    from app.models.timeline_event import TimelineEvent


class Case(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "cases"

    firm_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("firms.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="intake")

    firm: Mapped["Firm"] = relationship(back_populates="cases")
    documents: Mapped[list["Document"]] = relationship(back_populates="case")
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(back_populates="case")
    draft_outputs: Mapped[list["DraftOutput"]] = relationship(back_populates="case")
    model_usage_logs: Mapped[list["ModelUsageLog"]] = relationship(back_populates="case")
