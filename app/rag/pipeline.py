import time
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.repositories.driver_repo import DriverRepository
from app.db.repositories.search_query_repo import SearchQueryRepository
from app.models.driver import Driver
from app.rag.llm_client import LLMClient
from app.rag.prompt_builder import build_ranking_prompt
from app.rag.retriever import RAGRetriever


class RAGPipeline:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.llm = LLMClient()
        self.retriever = RAGRetriever(session)

    async def run_nl_search(
        self,
        query: str,
        company_id: uuid.UUID,
        user_id: Optional[uuid.UUID],
        max_results: int = 10,
        query_type: str = "natural_language",
    ) -> tuple[list[Driver], str, int]:
        """
        Full RAG flow: embed → retrieve → prompt → rank → log → return.
        Returns (ranked_drivers, explanation, token_count).
        """
        start_ms = int(time.monotonic() * 1000)

        # 1. Embed the query
        query_embedding = await self.llm.get_embedding(query)

        # 2. Vector search for relevant chunks
        chunks = await self.retriever.search(query_embedding, settings.rag_top_k_chunks)

        # 3. Deduplicate driver_ids (first-occurrence order = most relevant first)
        driver_ids_ordered = list(dict.fromkeys(c.driver_id for c in chunks))

        # 4. Fetch full Driver objects
        driver_repo = DriverRepository(self.session)
        all_drivers = await driver_repo.get_multiple_by_ids(driver_ids_ordered)
        drivers_map = {d.id: d for d in all_drivers}

        # 5. Build prompt and call LLM
        prompt = build_ranking_prompt(query, chunks, max_results)
        result = await self.llm.rank_drivers(query, prompt, max_results)

        # 6. Build LLM-ranked driver list (filter unknown IDs defensively)
        ranked: list[Driver] = []
        for entry in result["ranked_drivers"]:
            try:
                did = uuid.UUID(entry["driver_id"])
            except (ValueError, KeyError):
                continue
            if did in drivers_map:
                ranked.append(drivers_map[did])

        latency_ms = int(time.monotonic() * 1000) - start_ms

        # 7. Log the search query for audit + analytics
        await self._log_search(
            company_id=company_id,
            user_id=user_id,
            query_type=query_type,
            query_text=query,
            drivers=ranked,
            explanation=result["explanation"],
            latency_ms=latency_ms,
            token_count=result["token_count"],
        )

        return ranked, result["explanation"], result["token_count"]

    async def _log_search(
        self,
        company_id: uuid.UUID,
        user_id: Optional[uuid.UUID],
        query_type: str,
        query_text: str,
        drivers: list[Driver],
        explanation: str,
        latency_ms: int,
        token_count: int,
    ) -> None:
        repo = SearchQueryRepository(self.session)
        await repo.create(
            company_id=company_id,
            user_id=user_id,
            query_type=query_type,
            query_text=query_text,
            driver_ids_returned=[d.id for d in drivers],
            llm_response=explanation,
            latency_ms=latency_ms,
            token_count=token_count,
        )
