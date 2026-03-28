from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.driver_season import DriverSeason


class Team(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "teams"

    ergast_constructor_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_season: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    seasons: Mapped[list["DriverSeason"]] = relationship("DriverSeason", back_populates="team")
