import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ShortlistCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ShortlistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ShortlistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str]
    driver_ids: Optional[list[uuid.UUID]]
    notes: Optional[dict]
    created_at: datetime
    updated_at: datetime


class AddDriversRequest(BaseModel):
    driver_ids: list[uuid.UUID]
    notes: Optional[dict[str, str]] = None
