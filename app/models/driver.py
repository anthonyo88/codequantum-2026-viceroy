import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.driver_season import DriverSeason
    from app.models.race_result import RaceResult


class Driver(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "drivers"

    # Identity
    ergast_driver_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    profile_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    license_grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    active_status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # pgvector embedding (1536 dims = text-embedding-3-large)
    embedding_vector: Mapped[Optional[list]] = mapped_column(Vector(1536), nullable=True)

    # Relationships
    career_stats: Mapped[Optional["DriverCareerStats"]] = relationship(
        "DriverCareerStats", back_populates="driver", uselist=False, cascade="all, delete-orphan"
    )
    seasons: Mapped[list["DriverSeason"]] = relationship(
        "DriverSeason", back_populates="driver", cascade="all, delete-orphan"
    )
    race_results: Mapped[list["RaceResult"]] = relationship(
        "RaceResult", back_populates="driver", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class DriverCareerStats(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "driver_career_stats"

    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )

    total_race_starts: Mapped[int] = mapped_column(Integer, default=0)
    total_wins: Mapped[int] = mapped_column(Integer, default=0)
    total_podiums: Mapped[int] = mapped_column(Integer, default=0)
    total_pole_positions: Mapped[int] = mapped_column(Integer, default=0)
    total_fastest_laps: Mapped[int] = mapped_column(Integer, default=0)
    total_championship_points: Mapped[float] = mapped_column(Float, default=0.0)
    championships_won: Mapped[int] = mapped_column(Integer, default=0)

    # Computed rates (updated on ingest)
    career_win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    career_podium_rate: Mapped[float] = mapped_column(Float, default=0.0)
    dnf_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_qualifying_position: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_finish_position: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    seasons_active: Mapped[Optional[list]] = mapped_column(ARRAY(Integer), nullable=True)
    teams_driven_for: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)

    active_status: Mapped[bool] = mapped_column(Boolean, default=True)
    last_race_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    driver: Mapped["Driver"] = relationship("Driver", back_populates="career_stats")
