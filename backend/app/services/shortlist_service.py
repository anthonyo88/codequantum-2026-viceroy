import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.repositories.shortlist_repo import ShortlistRepository
from app.models.shortlist import Shortlist
from app.schemas.shortlist import AddDriversRequest, ShortlistCreate, ShortlistUpdate


class ShortlistService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ShortlistRepository(session)

    async def create(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        request: ShortlistCreate,
    ) -> Shortlist:
        return await self.repo.create(
            company_id=company_id,
            created_by_user_id=user_id,
            name=request.name,
            description=request.description,
        )

    async def list_shortlists(self, company_id: uuid.UUID) -> list[Shortlist]:
        return await self.repo.list_by_company(company_id)

    async def get_shortlist(
        self, shortlist_id: uuid.UUID, company_id: uuid.UUID
    ) -> Shortlist:
        shortlist = await self.repo.get_by_id_and_company(shortlist_id, company_id)
        if shortlist is None:
            raise NotFoundError("Shortlist", str(shortlist_id))
        return shortlist

    async def update_shortlist(
        self,
        shortlist_id: uuid.UUID,
        company_id: uuid.UUID,
        request: ShortlistUpdate,
    ) -> Shortlist:
        shortlist = await self.get_shortlist(shortlist_id, company_id)
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        if updates:
            await self.repo.update(shortlist, **updates)
        return shortlist

    async def delete_shortlist(
        self, shortlist_id: uuid.UUID, company_id: uuid.UUID
    ) -> None:
        shortlist = await self.get_shortlist(shortlist_id, company_id)
        await self.repo.delete(shortlist)

    async def add_drivers(
        self,
        shortlist_id: uuid.UUID,
        company_id: uuid.UUID,
        request: AddDriversRequest,
    ) -> Shortlist:
        shortlist = await self.get_shortlist(shortlist_id, company_id)
        return await self.repo.add_drivers(shortlist, request.driver_ids, request.notes)

    async def remove_driver(
        self,
        shortlist_id: uuid.UUID,
        company_id: uuid.UUID,
        driver_id: uuid.UUID,
    ) -> Shortlist:
        shortlist = await self.get_shortlist(shortlist_id, company_id)
        if driver_id not in (shortlist.driver_ids or []):
            raise NotFoundError("Driver", str(driver_id))
        return await self.repo.remove_driver(shortlist, driver_id)
