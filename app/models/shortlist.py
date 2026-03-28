import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company


class Shortlist(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "shortlists"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # List of driver UUIDs stored as strings
    driver_ids: Mapped[Optional[list]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True, default=list)
    # Per-driver notes: {"driver_uuid": "note text"}
    notes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    company: Mapped["Company"] = relationship("Company", back_populates="shortlists")
