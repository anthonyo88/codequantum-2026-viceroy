import uuid
from typing import Optional

from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    message: str = Field(..., min_length=3, max_length=2000)
    session_id: Optional[str] = None
    context_driver_ids: Optional[list[uuid.UUID]] = None


class ChatQueryResponse(BaseModel):
    response: str
    session_id: str
    driver_ids_referenced: list[uuid.UUID]
    token_count: int


class RecommendRequest(BaseModel):
    criteria: str = Field(..., min_length=10, max_length=2000, description="Natural language description of what you're looking for in a driver")
    max_results: int = Field(5, ge=1, le=20)
