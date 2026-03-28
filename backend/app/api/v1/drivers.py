import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.driver import (
    DriverCompareResponse,
    DriverListResponse,
    DriverOut,
    DriverSeasonOut,
    DriverSummaryOut,
)
from app.schemas.search import DriverFilterRequest
from app.services.driver_service import DriverService

router = APIRouter()


@router.get("", response_model=DriverListResponse)
async def list_drivers(
    nationality: Optional[str] = Query(None),
    min_age: Optional[int] = Query(None, ge=16),
    max_age: Optional[int] = Query(None, le=60),
    min_wins: Optional[int] = Query(None, ge=0),
    max_wins: Optional[int] = Query(None),
    min_podiums: Optional[int] = Query(None, ge=0),
    min_championships: Optional[int] = Query(None, ge=0),
    active_only: bool = Query(False),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    filters = DriverFilterRequest(
        nationality=nationality,
        min_age=min_age,
        max_age=max_age,
        min_wins=min_wins,
        max_wins=max_wins,
        min_podiums=min_podiums,
        min_championships=min_championships,
        active_only=active_only,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )
    service = DriverService(db)
    drivers, total = await service.list_drivers(filters)
    return DriverListResponse(
        total=total,
        page=page,
        limit=limit,
        drivers=[DriverSummaryOut.model_validate(d) for d in drivers],
    )


@router.get("/compare", response_model=DriverCompareResponse)
async def compare_drivers(
    ids: str = Query(..., description="Comma-separated list of 2–4 driver UUIDs"),
    db: AsyncSession = Depends(get_db),
):
    driver_ids = [uuid.UUID(i.strip()) for i in ids.split(",")]
    service = DriverService(db)
    drivers = await service.compare_drivers(driver_ids)
    return DriverCompareResponse(drivers=[DriverOut.model_validate(d) for d in drivers])


@router.get("/{driver_id}", response_model=DriverOut)
async def get_driver(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = DriverService(db)
    driver = await service.get_driver(driver_id)
    return DriverOut.model_validate(driver)


@router.get("/{driver_id}/seasons", response_model=list[DriverSeasonOut])
async def get_driver_seasons(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = DriverService(db)
    seasons = await service.get_driver_seasons(driver_id)
    return [DriverSeasonOut.model_validate(s) for s in seasons]
