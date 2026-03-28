import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shortlist import Shortlist


class ShortlistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id_and_company(
        self, shortlist_id: uuid.UUID, company_id: uuid.UUID
    ) -> Optional[Shortlist]:
        result = await self.session.execute(
            select(Shortlist).where(
                Shortlist.id == shortlist_id,
                Shortlist.company_id == company_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_company(self, company_id: uuid.UUID) -> list[Shortlist]:
        result = await self.session.execute(
            select(Shortlist).where(Shortlist.company_id == company_id)
        )
        return list(result.scalars().all())

    async def create(
        self,
        company_id: uuid.UUID,
        created_by_user_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
    ) -> Shortlist:
        shortlist = Shortlist(
            company_id=company_id,
            created_by_user_id=created_by_user_id,
            name=name,
            description=description,
            driver_ids=[],
            notes={},
        )
        self.session.add(shortlist)
        await self.session.flush()
        await self.session.refresh(shortlist)
        return shortlist

    async def update(self, shortlist: Shortlist, **kwargs) -> Shortlist:
        for key, value in kwargs.items():
            setattr(shortlist, key, value)
        await self.session.flush()
        await self.session.refresh(shortlist)
        return shortlist

    async def delete(self, shortlist: Shortlist) -> None:
        await self.session.delete(shortlist)
        await self.session.flush()

    async def add_drivers(
        self,
        shortlist: Shortlist,
        driver_ids: list[uuid.UUID],
        notes: Optional[dict] = None,
    ) -> Shortlist:
        existing = shortlist.driver_ids or []
        # Deduplicate while preserving insertion order
        combined = list(dict.fromkeys(existing + driver_ids))
        shortlist.driver_ids = combined

        existing_notes = shortlist.notes or {}
        if notes:
            shortlist.notes = {**existing_notes, **notes}

        await self.session.flush()
        await self.session.refresh(shortlist)
        return shortlist

    async def remove_driver(
        self, shortlist: Shortlist, driver_id: uuid.UUID
    ) -> Shortlist:
        shortlist.driver_ids = [d for d in (shortlist.driver_ids or []) if d != driver_id]
        existing_notes = shortlist.notes or {}
        shortlist.notes = {k: v for k, v in existing_notes.items() if k != str(driver_id)}
        await self.session.flush()
        await self.session.refresh(shortlist)
        return shortlist
