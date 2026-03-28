import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company_user import CompanyUser
    from app.models.shortlist import Shortlist
    from app.models.search_query import SearchQuery


class CompanyType(str, enum.Enum):
    F1_TEAM = "f1_team"
    FORMULA2 = "formula2"
    FORMULA3 = "formula3"
    INDYCAR = "indycar"
    SPONSOR = "sponsor"
    OTHER = "other"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Company(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    company_type: Mapped[CompanyType] = mapped_column(
        Enum(CompanyType), default=CompanyType.OTHER
    )
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier), default=SubscriptionTier.FREE
    )
    contact_email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    query_quota_monthly: Mapped[int] = mapped_column(Integer, default=100)
    queries_used_this_month: Mapped[int] = mapped_column(Integer, default=0)

    users: Mapped[list["CompanyUser"]] = relationship(
        "CompanyUser", back_populates="company", cascade="all, delete-orphan"
    )
    shortlists: Mapped[list["Shortlist"]] = relationship(
        "Shortlist", back_populates="company", cascade="all, delete-orphan"
    )
    search_queries: Mapped[list["SearchQuery"]] = relationship(
        "SearchQuery", back_populates="company"
    )
