import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DriverCareerStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_race_starts: int
    total_wins: int
    total_podiums: int
    total_pole_positions: int
    total_fastest_laps: int
    total_championship_points: float
    championships_won: int
    career_win_rate: float
    career_podium_rate: float
    dnf_rate: float
    avg_qualifying_position: Optional[float]
    avg_finish_position: Optional[float]
    seasons_active: Optional[list[int]]
    teams_driven_for: Optional[list[str]]
    active_status: bool
    last_race_date: Optional[date]


class DriverOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_name: str
    last_name: str
    full_name: str
    nationality: Optional[str]
    date_of_birth: Optional[date]
    biography: Optional[str]
    profile_image_url: Optional[str]
    license_grade: Optional[str]
    active_status: bool
    career_stats: Optional[DriverCareerStatsOut]
    created_at: datetime
    updated_at: datetime


class DriverSummaryOut(BaseModel):
    """Lighter response for list endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    nationality: Optional[str]
    active_status: bool
    career_stats: Optional[DriverCareerStatsOut]


class DriverSeasonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    season_year: int
    championship_position: Optional[int]
    points: float
    wins: int
    podiums: int
    poles: int
    fastest_laps: int
    races_entered: int
    dnfs: int


class DriverListResponse(BaseModel):
    total: int
    page: int
    limit: int
    drivers: list[DriverSummaryOut]


class DriverCompareResponse(BaseModel):
    drivers: list[DriverOut]
