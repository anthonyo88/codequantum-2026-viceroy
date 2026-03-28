import uuid
from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.db.session import get_db
from app.models.company_user import CompanyUser, UserRole

# Re-export get_db as the standard DB dependency
DBSession = Depends(get_db)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncGenerator[AsyncSession, None]:
    yield db


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> CompanyUser:
    # Import here to avoid circular imports at module load time
    from app.core.auth import decode_token
    from app.db.repositories.company_repo import CompanyUserRepository

    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")
    user_id = uuid.UUID(payload["sub"])
    repo = CompanyUserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise UnauthorizedError("User not found")
    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> Optional[CompanyUser]:
    if token is None:
        return None
    try:
        return await get_current_user(token=token, db=db)
    except UnauthorizedError:
        return None


def require_role(*roles: UserRole):
    async def dependency(
        current_user: CompanyUser = Depends(get_current_user),
    ) -> CompanyUser:
        if current_user.role not in roles:
            raise ForbiddenError()
        return current_user

    return dependency
