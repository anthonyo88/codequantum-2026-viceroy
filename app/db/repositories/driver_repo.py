import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.driver import Driver, DriverCareerStats
from app.models.driver_season import DriverSeason
from app.schemas.search import DriverFilterRequest


class DriverRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, driver_id: uuid.UUID) -> Optional[Driver]:
        result = await self.session.execute(
            select(Driver)
            .options(selectinload(Driver.career_stats))
            .where(Driver.id == driver_id)
        )
        return result.scalar_one_or_none()

    async def get_seasons(self, driver_id: uuid.UUID) -> list[DriverSeason]:
        result = await self.session.execute(
            select(DriverSeason)
            .where(DriverSeason.driver_id == driver_id)
            .order_by(DriverSeason.season_year.desc())
        )
        return list(result.scalars().all())

    async def list_filtered(
        self, filters: DriverFilterRequest
    ) -> tuple[list[Driver], int]:
        from datetime import date, timedelta

        query = (
            select(Driver)
            .options(selectinload(Driver.career_stats))
            .join(Driver.career_stats, isouter=True)
        )

        if filters.nationality:
            query = query.where(
                func.lower(Driver.nationality) == filters.nationality.lower()
            )

        if filters.active_only:
            query = query.where(Driver.active_status.is_(True))

        today = date.today()

        if filters.min_age is not None:
            cutoff = today - timedelta(days=filters.min_age * 365)
            query = query.where(Driver.date_of_birth <= cutoff)

        if filters.max_age is not None:
            cutoff = today - timedelta(days=filters.max_age * 365)
            query = query.where(Driver.date_of_birth >= cutoff)

        if filters.min_wins is not None:
            query = query.where(DriverCareerStats.total_wins >= filters.min_wins)

        if filters.max_wins is not None:
            query = query.where(DriverCareerStats.total_wins <= filters.max_wins)

        if filters.min_podiums is not None:
            query = query.where(DriverCareerStats.total_podiums >= filters.min_podiums)

        if filters.min_championships is not None:
            query = query.where(DriverCareerStats.championships_won >= filters.min_championships)

        if filters.seasons_active:
            from sqlalchemy.dialects.postgresql import ARRAY
            import sqlalchemy as sa
            for year in filters.seasons_active:
                query = query.where(
                    DriverCareerStats.seasons_active.contains([year])
                )

        # Sorting
        sort_map = {
            "win_rate": DriverCareerStats.career_win_rate,
            "total_wins": DriverCareerStats.total_wins,
            "total_podiums": DriverCareerStats.total_podiums,
            "championships_won": DriverCareerStats.championships_won,
            "total_race_starts": DriverCareerStats.total_race_starts,
        }
        sort_col = sort_map.get(filters.sort_by or "total_wins", DriverCareerStats.total_wins)
        if filters.sort_order == "asc":
            query = query.order_by(sort_col.asc().nullslast())
        else:
            query = query.order_by(sort_col.desc().nullslast())

        # Count
        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        # Paginate
        offset = (filters.page - 1) * filters.limit
        query = query.offset(offset).limit(filters.limit)

        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_multiple_by_ids(self, driver_ids: list[uuid.UUID]) -> list[Driver]:
        result = await self.session.execute(
            select(Driver)
            .options(selectinload(Driver.career_stats))
            .where(Driver.id.in_(driver_ids))
        )
        return list(result.scalars().all())
