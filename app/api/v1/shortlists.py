import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.company_user import CompanyUser
from app.schemas.shortlist import AddDriversRequest, ShortlistCreate, ShortlistOut, ShortlistUpdate
from app.services.shortlist_service import ShortlistService

router = APIRouter()


@router.post("", response_model=ShortlistOut, status_code=status.HTTP_201_CREATED)
async def create_shortlist(
    request: ShortlistCreate,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShortlistService(db)
    shortlist = await service.create(current_user.company_id, current_user.id, request)
    return ShortlistOut.model_validate(shortlist)


@router.get("", response_model=list[ShortlistOut])
async def list_shortlists(
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShortlistService(db)
    shortlists = await service.list_shortlists(current_user.company_id)
    return [ShortlistOut.model_validate(s) for s in shortlists]


@router.get("/{shortlist_id}", response_model=ShortlistOut)
async def get_shortlist(
    shortlist_id: uuid.UUID,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShortlistService(db)
    shortlist = await service.get_shortlist(shortlist_id, current_user.company_id)
    return ShortlistOut.model_validate(shortlist)


@router.patch("/{shortlist_id}", response_model=ShortlistOut)
async def update_shortlist(
    shortlist_id: uuid.UUID,
    request: ShortlistUpdate,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShortlistService(db)
    shortlist = await service.update_shortlist(shortlist_id, current_user.company_id, request)
    return ShortlistOut.model_validate(shortlist)


@router.delete("/{shortlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shortlist(
    shortlist_id: uuid.UUID,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShortlistService(db)
    await service.delete_shortlist(shortlist_id, current_user.company_id)
    return None


@router.post("/{shortlist_id}/drivers", response_model=ShortlistOut)
async def add_drivers(
    shortlist_id: uuid.UUID,
    request: AddDriversRequest,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShortlistService(db)
    shortlist = await service.add_drivers(shortlist_id, current_user.company_id, request)
    return ShortlistOut.model_validate(shortlist)


@router.delete("/{shortlist_id}/drivers/{driver_id}", response_model=ShortlistOut)
async def remove_driver(
    shortlist_id: uuid.UUID,
    driver_id: uuid.UUID,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShortlistService(db)
    shortlist = await service.remove_driver(shortlist_id, current_user.company_id, driver_id)
    return ShortlistOut.model_validate(shortlist)
