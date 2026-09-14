from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.common import CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.user import User


class Firm(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "firms"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="firm")
    cases: Mapped[list["Case"]] = relationship(back_populates="firm")
