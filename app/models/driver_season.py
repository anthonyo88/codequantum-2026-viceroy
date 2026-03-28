import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.driver import Driver
    from app.models.team import Team


class DriverSeason(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "driver_seasons"

    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False
    )
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True
    )
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    championship_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    points: Mapped[float] = mapped_column(Float, default=0.0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    podiums: Mapped[int] = mapped_column(Integer, default=0)
    poles: Mapped[int] = mapped_column(Integer, default=0)
    fastest_laps: Mapped[int] = mapped_column(Integer, default=0)
    races_entered: Mapped[int] = mapped_column(Integer, default=0)
    dnfs: Mapped[int] = mapped_column(Integer, default=0)

    # Head-to-head vs teammate
    teammate_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    teammate_qualifying_delta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    teammate_race_delta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    driver: Mapped["Driver"] = relationship("Driver", back_populates="seasons")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="seasons")
