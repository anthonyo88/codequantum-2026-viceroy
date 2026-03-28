"""Embedding generation Celery tasks — synchronous to avoid asyncio/Celery fork issues."""

import uuid

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from app.config import settings
from app.ingestion.chunker import build_chunks
from app.models.document_chunk import DocumentChunk
from app.models.driver import Driver
from app.models.driver_season import DriverSeason
from app.rag.llm_client import _get_st_model
from app.workers.celery_app import celery_app

# Derive a psycopg2 (sync) URL from the asyncpg URL in settings
_SYNC_URL = settings.database_url.replace(
    "postgresql+asyncpg://", "postgresql+psycopg2://"
)


def _make_sync_session() -> tuple[Session, any]:
    engine = create_engine(_SYNC_URL)
    factory = sessionmaker(engine)
    return factory(), engine


@celery_app.task(name="embeddings.generate_for_driver")
def generate_driver_embedding(driver_id: str) -> None:
    session, engine = _make_sync_session()
    try:
        driver = session.execute(
            select(Driver)
            .options(selectinload(Driver.career_stats))
            .where(Driver.id == uuid.UUID(driver_id))
        ).scalar_one_or_none()

        if driver is None:
            return

        seasons = list(
            session.execute(
                select(DriverSeason)
                .where(DriverSeason.driver_id == driver.id)
                .order_by(DriverSeason.season_year.desc())
            ).scalars().all()
        )

        session.execute(delete(DocumentChunk).where(DocumentChunk.driver_id == driver.id))

        chunks = build_chunks(driver, seasons)

        model = _get_st_model()
        for chunk in chunks:
            chunk.embedding = model.encode(chunk.content).tolist()
            session.add(chunk)

        session.commit()
    finally:
        session.close()
        engine.dispose()


@celery_app.task(name="embeddings.rebuild_all")
def rebuild_all_embeddings() -> None:
    session, engine = _make_sync_session()
    try:
        driver_ids = [str(row) for row in session.execute(select(Driver.id)).scalars().all()]
    finally:
        session.close()
        engine.dispose()

    for did in driver_ids:
        generate_driver_embedding.delay(did)
