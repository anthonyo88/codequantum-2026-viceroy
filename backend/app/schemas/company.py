import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.company import CompanyType, SubscriptionTier
from app.models.company_user import UserRole


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    company_type: CompanyType
    subscription_tier: SubscriptionTier
    contact_email: str
    is_verified: bool
    query_quota_monthly: int
    queries_used_this_month: int
    created_at: datetime


class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = None
    company_type: Optional[CompanyType] = None


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.SCOUT
