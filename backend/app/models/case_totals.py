import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.common import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.case import Case


class CaseTotals(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "case_totals"

    case_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, unique=True
    )
    total_billed: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_wages: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    case: Mapped["Case"] = relationship(back_populates="totals")
