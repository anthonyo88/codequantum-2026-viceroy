from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_token_pair, hash_password, verify_password
from app.core.exceptions import ConflictError, UnauthorizedError
from app.db.repositories.company_repo import CompanyRepository, CompanyUserRepository
from app.models.company import CompanyType, SubscriptionTier
from app.models.company_user import CompanyUser, UserRole
from app.schemas.auth import CompanyRegisterRequest, LoginRequest, RefreshRequest


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.company_repo = CompanyRepository(session)
        self.user_repo = CompanyUserRepository(session)

    async def register(
        self, request: CompanyRegisterRequest
    ) -> tuple[CompanyUser, str, str]:
        if await self.company_repo.get_by_contact_email(request.email):
            raise ConflictError("A company with this email already exists")
        if await self.user_repo.get_by_email(request.email):
            raise ConflictError("A user with this email already exists")

        company = await self.company_repo.create(
            name=request.company_name,
            contact_email=request.email,
            company_type=CompanyType.OTHER,
            subscription_tier=SubscriptionTier.FREE,
        )
        user = await self.user_repo.create(
            company_id=company.id,
            email=request.email,
            hashed_password=hash_password(request.password),
            role=UserRole.ADMIN,
        )
        access, refresh = create_token_pair(str(user.id), str(company.id))
        return user, access, refresh

    async def login(self, request: LoginRequest) -> tuple[CompanyUser, str, str]:
        user = await self.user_repo.get_by_email(request.email)
        if user is None or not verify_password(request.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        await self.user_repo.update_last_login(user)
        access, refresh = create_token_pair(str(user.id), str(user.company_id))
        return user, access, refresh

    async def refresh(self, request: RefreshRequest) -> tuple[str, str]:
        from app.core.auth import decode_token

        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        import uuid
        user = await self.user_repo.get_by_id(uuid.UUID(payload["sub"]))
        if user is None:
            raise UnauthorizedError("User not found")

        return create_token_pair(str(user.id), str(user.company_id))
