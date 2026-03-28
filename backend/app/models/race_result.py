import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.driver import Driver


class Circuit(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "circuits"

    ergast_circuit_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    race_results: Mapped[list["RaceResult"]] = relationship("RaceResult", back_populates="circuit")


class RaceResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "race_results"

    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False
    )
    circuit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("circuits.id", ondelete="SET NULL"), nullable=True
    )
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    race_name: Mapped[str] = mapped_column(String(200), nullable=False)
    race_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    grid_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    finish_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    points: Mapped[float] = mapped_column(Float, default=0.0)
    # Finished / DNF / DNS / DSQ / Retired
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fastest_lap: Mapped[bool] = mapped_column(Boolean, default=False)
    lap_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    team_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    driver: Mapped["Driver"] = relationship("Driver", back_populates="race_results")
    circuit: Mapped[Optional["Circuit"]] = relationship("Circuit", back_populates="race_results")
