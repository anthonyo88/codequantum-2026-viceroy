import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.repositories.driver_repo import DriverRepository
from app.models.driver import Driver
from app.models.driver_season import DriverSeason
from app.schemas.search import DriverFilterRequest


class DriverService:
    def __init__(self, session: AsyncSession):
        self.repo = DriverRepository(session)

    async def get_driver(self, driver_id: uuid.UUID) -> Driver:
        driver = await self.repo.get_by_id(driver_id)
        if driver is None:
            raise NotFoundError("Driver", str(driver_id))
        return driver

    async def get_driver_seasons(self, driver_id: uuid.UUID) -> list[DriverSeason]:
        await self.get_driver(driver_id)  # 404 if not found
        return await self.repo.get_seasons(driver_id)

    async def list_drivers(self, filters: DriverFilterRequest) -> tuple[list[Driver], int]:
        return await self.repo.list_filtered(filters)

    async def compare_drivers(self, driver_ids: list[uuid.UUID]) -> list[Driver]:
        if len(driver_ids) < 2 or len(driver_ids) > 4:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Provide 2–4 driver IDs to compare")
        drivers = await self.repo.get_multiple_by_ids(driver_ids)
        if len(drivers) != len(driver_ids):
            missing = set(driver_ids) - {d.id for d in drivers}
            raise NotFoundError("Driver", str(missing))
        return drivers
