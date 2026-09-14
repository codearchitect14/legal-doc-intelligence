import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.common import CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.firm import Firm


class UserRole(str, enum.Enum):
    LAWYER = "lawyer"
    PARALEGAL = "paralegal"
    FIRM_ADMIN = "firm_admin"
    SYSTEM_ADMIN = "system_admin"


class User(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "users"

    firm_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("firms.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)

    firm: Mapped["Firm"] = relationship(back_populates="users")
