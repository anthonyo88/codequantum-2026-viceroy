import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user, require_role
from app.models.company_user import CompanyUser, UserRole
from app.schemas.auth import UserOut
from app.schemas.company import CompanyOut, CompanyUpdateRequest, CreateUserRequest
from app.services.company_service import CompanyService

router = APIRouter()


@router.get("/me", response_model=CompanyOut)
async def get_my_company(
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    company = await service.get_my_company(current_user.company_id)
    return CompanyOut.model_validate(company)


@router.patch("/me", response_model=CompanyOut)
async def update_my_company(
    request: CompanyUpdateRequest,
    current_user: CompanyUser = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    company = await service.update_my_company(current_user.company_id, request)
    return CompanyOut.model_validate(company)


@router.get("/me/users", response_model=list[UserOut])
async def list_users(
    current_user: CompanyUser = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    users = await service.list_users(current_user.company_id)
    return [UserOut.model_validate(u) for u in users]


@router.post("/me/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    current_user: CompanyUser = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    user = await service.create_user(
        company_id=current_user.company_id,
        email=str(request.email),
        password=request.password,
        role=request.role,
    )
    return UserOut.model_validate(user)


@router.delete("/me/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    current_user: CompanyUser = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    await service.delete_user(
        company_id=current_user.company_id,
        user_id=user_id,
        requesting_user_id=current_user.id,
    )
    return None
