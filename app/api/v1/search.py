from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user_optional
from app.models.company_user import CompanyUser
from app.schemas.driver import DriverListResponse, DriverSummaryOut
from app.schemas.search import DriverFilterRequest
from app.services.company_service import CompanyService
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/filter", response_model=DriverListResponse)
async def filter_drivers(
    request: DriverFilterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[CompanyUser] = Depends(get_current_user_optional),
):
    if current_user is not None:
        company_service = CompanyService(db)
        await company_service.check_and_increment_quota(current_user.company_id)

    service = SearchService(db)
    drivers, total = await service.filter_drivers(request)
    return DriverListResponse(
        total=total,
        page=request.page,
        limit=request.limit,
        drivers=[DriverSummaryOut.model_validate(d) for d in drivers],
    )
