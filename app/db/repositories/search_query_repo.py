import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_query import SearchQuery


class SearchQueryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        company_id: uuid.UUID,
        user_id: Optional[uuid.UUID],
        query_type: str,
        query_text: Optional[str],
        driver_ids_returned: Optional[list[uuid.UUID]],
        llm_response: Optional[str],
        latency_ms: Optional[int],
        token_count: Optional[int],
    ) -> SearchQuery:
        record = SearchQuery(
            company_id=company_id,
            user_id=user_id,
            query_type=query_type,
            query_text=query_text,
            driver_ids_returned=driver_ids_returned or [],
            llm_response=llm_response,
            latency_ms=latency_ms,
            token_count=token_count,
        )
        self.session.add(record)
        await self.session.flush()
        return record
