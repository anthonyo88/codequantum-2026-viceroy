from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.driver_repo import DriverRepository
from app.models.driver import Driver
from app.schemas.search import DriverFilterRequest


class SearchService:
    def __init__(self, session: AsyncSession):
        self.repo = DriverRepository(session)

    async def filter_drivers(
        self, filters: DriverFilterRequest
    ) -> tuple[list[Driver], int]:
        return await self.repo.list_filtered(filters)
