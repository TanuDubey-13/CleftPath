from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging
from app.db.session import get_db
from app.middleware.cors import setup_cors
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.schemas.health import HealthResponse
from app.services.health_service import HealthService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging(debug=settings.DEBUG)
    logger.info(f"Starting {settings.PROJECT_NAME} API v{settings.VERSION} [{settings.ENVIRONMENT}]")
    logger.info(f"Tagline: '{settings.TAGLINE}'")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME} API")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Full-stack, AI-assisted healthcare technology platform supporting "
        "individuals and families across the longitudinal cleft lip and palate journey.\n\n"
        f"**Tagline:** *\"{settings.TAGLINE}\"*"
    ),
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup Middlewares & Exception Handlers
setup_cors(app)
app.add_middleware(RequestLoggingMiddleware)
setup_exception_handlers(app)

# Mount Root Health Endpoint (convenience alias to /api/v1/health)
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Root Health Check",
    include_in_schema=True,
)
async def root_health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    return await HealthService.check_health(db)


# Mount API v1 Routes
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
