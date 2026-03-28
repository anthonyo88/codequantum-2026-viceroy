"""Embedding generation Celery tasks."""

import asyncio
import uuid

from sqlalchemy import delete

from app.db.repositories.driver_repo import DriverRepository
from app.db.session import AsyncSessionLocal
from app.ingestion.chunker import build_chunks
from app.models.document_chunk import DocumentChunk
from app.rag.llm_client import LLMClient
from app.workers.celery_app import celery_app


@celery_app.task(name="embeddings.generate_for_driver")
def generate_driver_embedding(driver_id: str) -> None:
    asyncio.run(_async_generate(driver_id))


@celery_app.task(name="embeddings.rebuild_all")
def rebuild_all_embeddings() -> None:
    asyncio.run(_async_rebuild_all())


async def _async_generate(driver_id: str) -> None:
    async with AsyncSessionLocal() as session:
        driver_repo = DriverRepository(session)
        driver = await driver_repo.get_by_id(uuid.UUID(driver_id))
        if driver is None:
            return

        seasons = await driver_repo.get_seasons(driver.id)

        # Remove stale chunks before regenerating
        await session.execute(
            delete(DocumentChunk).where(DocumentChunk.driver_id == driver.id)
        )

        chunks = build_chunks(driver, seasons)

        llm = LLMClient()
        for chunk in chunks:
            chunk.embedding = await llm.get_embedding(chunk.content)
            session.add(chunk)

        await session.commit()


async def _async_rebuild_all() -> None:
    from sqlalchemy import select
    from app.models.driver import Driver

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Driver.id))
        driver_ids = [str(row[0]) for row in result.all()]

    for did in driver_ids:
        generate_driver_embedding.delay(did)
