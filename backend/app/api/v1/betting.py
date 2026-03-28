import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.company_user import CompanyUser
from app.rag.demo_cache import get_demo_cache
from app.rag.llm_client import LLMClient
from app.rag.prompt_builder import build_betting_prompt
from app.rag.retriever import RAGRetriever
from app.config import settings
from app.db.repositories.search_query_repo import SearchQueryRepository
from app.schemas.betting import BetPick, BettingRequest, BettingResponse
from app.services.company_service import CompanyService

router = APIRouter()


@router.post("/predict", response_model=BettingResponse)
async def predict_bets(
    request: BettingRequest,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_service = CompanyService(db)
    await company_service.check_and_increment_quota(current_user.company_id)

    # Demo cache check — return instantly if query matches a pre-answered question
    cached = await get_demo_cache().check_betting(request.race_context)
    if cached:
        picks = [
            BetPick(**p)
            for p in cached["picks"][: request.max_picks]
            if _is_valid_pick(p)
        ]
        repo = SearchQueryRepository(db)
        await repo.create(
            company_id=current_user.company_id,
            user_id=current_user.id,
            query_type="betting",
            query_text=request.race_context,
            driver_ids_returned=[],
            llm_response=cached["summary"],
            latency_ms=0,
            token_count=0,
        )
        return BettingResponse(
            summary=cached["summary"],
            picks=picks,
            token_count=0,
        )

    llm = LLMClient()
    retriever = RAGRetriever(db)

    query_embedding = await llm.get_embedding(request.race_context)
    chunks = await retriever.search(query_embedding, settings.rag_top_k_chunks)

    prompt = build_betting_prompt(request.race_context, chunks, request.max_picks)
    result = await llm.get_betting_prediction(request.race_context, prompt, request.max_picks)

    picks = [BetPick(**p) for p in result["picks"] if _is_valid_pick(p)]

    repo = SearchQueryRepository(db)
    await repo.create(
        company_id=current_user.company_id,
        user_id=current_user.id,
        query_type="betting",
        query_text=request.race_context,
        driver_ids_returned=[],
        llm_response=result["summary"],
        latency_ms=0,
        token_count=result["token_count"],
    )

    return BettingResponse(
        summary=result["summary"],
        picks=picks,
        token_count=result["token_count"],
    )


def _is_valid_pick(pick: dict) -> bool:
    return all(k in pick for k in ("driver_id", "driver_name", "bet_type", "confidence", "reason"))
