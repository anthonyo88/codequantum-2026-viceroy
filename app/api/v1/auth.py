from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.company_user import CompanyUser
from app.schemas.auth import CompanyRegisterRequest, LoginRequest, RefreshRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: CompanyRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    _, access, refresh = await service.register(request)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    _, access, refresh = await service.login(request)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    access, refresh = await service.refresh(request)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    _current_user: CompanyUser = Depends(get_current_user),
):
    # Stateless JWT — token invalidation is client-side in Phase 2.
    # Phase 3 will add a token blacklist backed by Redis.
    return None
