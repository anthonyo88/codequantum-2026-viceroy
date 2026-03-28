import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company, CompanyType, SubscriptionTier
from app.models.company_user import CompanyUser, UserRole


class CompanyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_contact_email(self, email: str) -> Optional[Company]:
        result = await self.session.execute(
            select(Company).where(Company.contact_email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        result = await self.session.execute(
            select(Company)
            .where(Company.id == company_id)
            .options(selectinload(Company.users))
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        contact_email: str,
        company_type: CompanyType = CompanyType.OTHER,
        subscription_tier: SubscriptionTier = SubscriptionTier.FREE,
    ) -> Company:
        company = Company(
            name=name,
            contact_email=contact_email,
            company_type=company_type,
            subscription_tier=subscription_tier,
        )
        self.session.add(company)
        await self.session.flush()
        return company

    async def update(self, company: Company, **kwargs) -> Company:
        for key, value in kwargs.items():
            setattr(company, key, value)
        await self.session.flush()
        return company

    async def increment_query_count(self, company_id: uuid.UUID) -> None:
        await self.session.execute(
            update(Company)
            .where(Company.id == company_id)
            .values(queries_used_this_month=Company.queries_used_this_month + 1)
        )

    async def reset_quota_all(self) -> int:
        result = await self.session.execute(
            update(Company).values(queries_used_this_month=0)
        )
        return result.rowcount


class CompanyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> Optional[CompanyUser]:
        result = await self.session.execute(
            select(CompanyUser)
            .where(CompanyUser.email == email)
            .options(selectinload(CompanyUser.company))
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[CompanyUser]:
        result = await self.session.execute(
            select(CompanyUser)
            .where(CompanyUser.id == user_id)
            .options(selectinload(CompanyUser.company))
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_company(
        self, user_id: uuid.UUID, company_id: uuid.UUID
    ) -> Optional[CompanyUser]:
        result = await self.session.execute(
            select(CompanyUser).where(
                CompanyUser.id == user_id,
                CompanyUser.company_id == company_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_company(self, company_id: uuid.UUID) -> list[CompanyUser]:
        result = await self.session.execute(
            select(CompanyUser).where(CompanyUser.company_id == company_id)
        )
        return list(result.scalars().all())

    async def create(
        self,
        company_id: uuid.UUID,
        email: str,
        hashed_password: str,
        role: UserRole = UserRole.SCOUT,
    ) -> CompanyUser:
        user = CompanyUser(
            company_id=company_id,
            email=email,
            hashed_password=hashed_password,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def delete(self, user: CompanyUser) -> None:
        await self.session.delete(user)
        await self.session.flush()

    async def update_last_login(self, user: CompanyUser) -> None:
        user.last_login = datetime.now(UTC)
        await self.session.flush()
