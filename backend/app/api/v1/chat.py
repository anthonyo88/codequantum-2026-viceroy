import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.driver_repo import DriverRepository
from app.db.repositories.search_query_repo import SearchQueryRepository
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.company_user import CompanyUser
from app.rag.demo_cache import get_demo_cache
from app.rag.llm_client import LLMClient
from app.rag.prompt_builder import build_ranking_prompt
from app.rag.retriever import RAGRetriever
from app.config import settings
from app.schemas.chat import ChatQueryResponse
from app.services.company_service import CompanyService

router = APIRouter()


class ChatSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    limit: int = Field(5, ge=1, le=20)


@router.post("/search", response_model=ChatQueryResponse)
async def nl_search(
    request: ChatSearchRequest,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_service = CompanyService(db)
    await company_service.check_and_increment_quota(current_user.company_id)

    # 1. Demo cache check — return instantly on a hit (same pattern as betting)
    cached = await get_demo_cache().check_driver(request.query)
    if cached:
        driver_repo = DriverRepository(db)
        drivers = await driver_repo.get_by_full_names(cached["driver_names"])

        repo = SearchQueryRepository(db)
        await repo.create(
            company_id=current_user.company_id,
            user_id=current_user.id,
            query_type="natural_language",
            query_text=request.query,
            driver_ids_returned=[d.id for d in drivers],
            llm_response=cached["answer"],
            latency_ms=0,
            token_count=0,
        )

        return ChatQueryResponse(
            response=cached["answer"],
            session_id=str(uuid.uuid4()),
            driver_ids_referenced=[d.id for d in drivers],
            token_count=0,
        )

    # 2. Cache miss — full RAG pipeline
    llm = LLMClient()
    retriever = RAGRetriever(db)

    query_embedding = await llm.get_embedding(request.query)
    chunks = await retriever.search(query_embedding, settings.rag_top_k_chunks)

    driver_repo = DriverRepository(db)
    driver_ids_ordered = list(dict.fromkeys(c.driver_id for c in chunks))
    all_drivers = await driver_repo.get_multiple_by_ids(driver_ids_ordered)
    drivers_map = {d.id: d for d in all_drivers}

    prompt = build_ranking_prompt(request.query, chunks, request.limit)
    result = await llm.rank_drivers(request.query, prompt, request.limit)

    ranked = []
    for entry in result["ranked_drivers"]:
        try:
            did = uuid.UUID(entry["driver_id"])
        except (ValueError, KeyError):
            continue
        if did in drivers_map:
            ranked.append(drivers_map[did])

    repo = SearchQueryRepository(db)
    await repo.create(
        company_id=current_user.company_id,
        user_id=current_user.id,
        query_type="natural_language",
        query_text=request.query,
        driver_ids_returned=[d.id for d in ranked],
        llm_response=result["explanation"],
        latency_ms=0,
        token_count=result["token_count"],
    )

    return ChatQueryResponse(
        response=result["explanation"],
        session_id=str(uuid.uuid4()),
        driver_ids_referenced=[d.id for d in ranked],
        token_count=result["token_count"],
    )


@router.post("/recommend", response_model=ChatQueryResponse)
async def recommend(
    request: ChatSearchRequest,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Alias for /search — same logic, same demo cache, same schema."""
    return await nl_search(request, current_user, db)
