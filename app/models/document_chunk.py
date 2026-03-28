import uuid
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class DocumentChunk(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_chunks"

    driver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=True
    )
    # driver_bio / season_summary / race_result / general
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(768), nullable=True)
    # Extra context: season year, circuit, etc.
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    # Track which embedding model was used (for future upgrades)
    embedding_model: Mapped[str] = mapped_column(
        String(100), default="text-embedding-3-large", nullable=False
    )
