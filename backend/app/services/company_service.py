import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, QuotaExceededError
from app.db.repositories.company_repo import CompanyRepository, CompanyUserRepository
from app.models.company import Company
from app.models.company_user import CompanyUser, UserRole
from app.schemas.company import CompanyUpdateRequest


class CompanyService:
    def __init__(self, session: AsyncSession) -> None:
        self.company_repo = CompanyRepository(session)
        self.user_repo = CompanyUserRepository(session)

    async def get_my_company(self, company_id: uuid.UUID) -> Company:
        company = await self.company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("Company", str(company_id))
        return company

    async def update_my_company(
        self, company_id: uuid.UUID, request: CompanyUpdateRequest
    ) -> Company:
        company = await self.get_my_company(company_id)
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        if updates:
            await self.company_repo.update(company, **updates)
        return company

    async def list_users(self, company_id: uuid.UUID) -> list[CompanyUser]:
        return await self.user_repo.list_by_company(company_id)

    async def create_user(
        self,
        company_id: uuid.UUID,
        email: str,
        password: str,
        role: UserRole,
    ) -> CompanyUser:
        if await self.user_repo.get_by_email(email):
            raise ConflictError("A user with this email already exists")
        return await self.user_repo.create(
            company_id=company_id,
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )

    async def delete_user(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> None:
        if user_id == requesting_user_id:
            raise ForbiddenError("Cannot remove your own account")
        user = await self.user_repo.get_by_id_and_company(user_id, company_id)
        if user is None:
            raise NotFoundError("User", str(user_id))
        await self.user_repo.delete(user)

    async def check_and_increment_quota(self, company_id: uuid.UUID) -> None:
        company = await self.company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("Company", str(company_id))
        if company.queries_used_this_month >= company.query_quota_monthly:
            raise QuotaExceededError()
        await self.company_repo.increment_query_count(company_id)
