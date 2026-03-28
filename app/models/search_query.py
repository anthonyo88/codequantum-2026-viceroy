import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company


class SearchQuery(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "search_queries"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    # filter / natural_language / comparison / recommendation
    query_type: Mapped[str] = mapped_column(String(50), nullable=False)
    query_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    filters_applied: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    driver_ids_returned: Mapped[Optional[list]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    llm_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="search_queries")
