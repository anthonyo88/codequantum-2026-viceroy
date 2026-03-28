import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.company_user import CompanyUser
from app.rag.pipeline import RAGPipeline
from app.schemas.chat import ChatQueryResponse, RecommendRequest
from app.schemas.search import NaturalLanguageSearchRequest
from app.services.company_service import CompanyService

router = APIRouter()


@router.post("/search", response_model=ChatQueryResponse)
async def nl_search(
    request: NaturalLanguageSearchRequest,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_service = CompanyService(db)
    await company_service.check_and_increment_quota(current_user.company_id)

    pipeline = RAGPipeline(db)
    drivers, explanation, token_count = await pipeline.run_nl_search(
        query=request.query,
        company_id=current_user.company_id,
        user_id=current_user.id,
        max_results=request.limit,
        query_type="natural_language",
    )

    return ChatQueryResponse(
        response=explanation,
        session_id=str(uuid.uuid4()),
        driver_ids_referenced=[d.id for d in drivers],
        token_count=token_count,
    )


@router.post("/recommend", response_model=ChatQueryResponse)
async def recommend(
    request: RecommendRequest,
    current_user: CompanyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_service = CompanyService(db)
    await company_service.check_and_increment_quota(current_user.company_id)

    pipeline = RAGPipeline(db)
    drivers, explanation, token_count = await pipeline.run_nl_search(
        query=request.criteria,
        company_id=current_user.company_id,
        user_id=current_user.id,
        max_results=request.max_results,
        query_type="recommendation",
    )

    return ChatQueryResponse(
        response=explanation,
        session_id=str(uuid.uuid4()),
        driver_ids_referenced=[d.id for d in drivers],
        token_count=token_count,
    )
