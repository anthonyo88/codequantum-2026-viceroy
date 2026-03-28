"""Background Celery task for triggering ingestion asynchronously."""

import asyncio
from pathlib import Path

from app.workers.celery_app import celery_app


@celery_app.task(name="ingestion.run_full")
def run_full_ingestion(data_dir: str = "data/raw", truncate_first: bool = True) -> dict:
    from app.db.session import AsyncSessionLocal
    from app.ingestion.pipeline import run_ingestion

    async def _run():
        async with AsyncSessionLocal() as session:
            return await run_ingestion(
                data_dir=Path(data_dir),
                session=session,
                truncate_first=truncate_first,
            )

    return asyncio.run(_run())
