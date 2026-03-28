from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.company_repo import CompanyRepository
from app.db.session import get_db
from app.ingestion.pipeline import run_ingestion
from app.models.document_chunk import DocumentChunk
from app.models.driver import Driver

router = APIRouter()


class IngestRequest(BaseModel):
    data_dir: str = "data/raw"
    truncate_first: bool = True


class QuotaResetRequest(BaseModel):
    company_email: Optional[EmailStr] = None


@router.post("/ingest/drivers")
async def ingest_drivers(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger CSV ingestion from data_dir.
    Drop the CSV files in data/raw/ then call this endpoint.
    """
    data_dir = Path(request.data_dir)
    if not data_dir.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Data directory '{data_dir}' does not exist. "
                   f"Place your CSV files there and retry.",
        )
    try:
        summary = await run_ingestion(
            data_dir=data_dir,
            session=db,
            truncate_first=request.truncate_first,
        )
        return {"status": "success", "summary": summary}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")


@router.post("/quota/reset")
async def reset_quota(
    request: QuotaResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset queries_used_this_month.
    Pass company_email to reset one company, omit it to reset all.
    """
    repo = CompanyRepository(db)

    if request.company_email:
        company = await repo.get_by_contact_email(str(request.company_email))
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        await repo.update(company, queries_used_this_month=0)
        return {"reset": 1, "company": company.name}

    count = await repo.reset_quota_all()
    return {"reset": count}


@router.get("/embeddings/status")
async def embedding_status(db: AsyncSession = Depends(get_db)):
    """
    Returns how many drivers have embeddings generated.
    Use this to confirm the system is ready before demoing chat/search.
    """
    total_drivers_result = await db.execute(select(func.count()).select_from(Driver))
    total_drivers = total_drivers_result.scalar_one()

    drivers_embedded_result = await db.execute(
        select(func.count(func.distinct(DocumentChunk.driver_id))).where(
            DocumentChunk.embedding.is_not(None)
        )
    )
    drivers_embedded = drivers_embedded_result.scalar_one()

    total_chunks_result = await db.execute(
        select(func.count()).select_from(DocumentChunk)
    )
    total_chunks = total_chunks_result.scalar_one()

    chunks_embedded_result = await db.execute(
        select(func.count()).select_from(DocumentChunk).where(
            DocumentChunk.embedding.is_not(None)
        )
    )
    chunks_embedded = chunks_embedded_result.scalar_one()

    return {
        "total_drivers": total_drivers,
        "drivers_embedded": drivers_embedded,
        "drivers_pending": total_drivers - drivers_embedded,
        "total_chunks": total_chunks,
        "chunks_embedded": chunks_embedded,
        "chunks_pending": total_chunks - chunks_embedded,
        "ready": total_drivers > 0 and drivers_embedded >= total_drivers,
    }


@router.get("/health")
async def admin_health():
    return {"status": "ok"}
