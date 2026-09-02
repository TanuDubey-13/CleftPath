from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System and Database Health Check",
    description="Returns service status, database connectivity, and pgvector extension readiness.",
)
async def get_health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    return await HealthService.check_health(db)
