from typing import Optional

from pydantic import BaseModel, Field


class DriverFilterRequest(BaseModel):
    nationality: Optional[str] = None
    min_age: Optional[int] = Field(None, ge=16, le=60)
    max_age: Optional[int] = Field(None, ge=16, le=60)
    min_wins: Optional[int] = Field(None, ge=0)
    max_wins: Optional[int] = None
    min_podiums: Optional[int] = Field(None, ge=0)
    min_championships: Optional[int] = Field(None, ge=0)
    seasons_active: Optional[list[int]] = None
    teams: Optional[list[str]] = None
    active_only: bool = False
    sort_by: Optional[str] = Field(
        None,
        description="Field to sort by: win_rate, total_wins, total_podiums, championships_won",
    )
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class NaturalLanguageSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
