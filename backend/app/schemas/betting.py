from pydantic import BaseModel, Field


class BettingRequest(BaseModel):
    race_context: str = Field(..., description="Race description, e.g. 'Monaco GP 2024, wet conditions'")
    max_picks: int = Field(5, ge=1, le=10)


class BetPick(BaseModel):
    driver_id: str
    driver_name: str
    bet_type: str   # "win" | "podium" | "points_finish"
    confidence: str  # "high" | "medium" | "low"
    reason: str


class BettingResponse(BaseModel):
    summary: str
    picks: list[BetPick]
    token_count: int
