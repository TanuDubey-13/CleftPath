import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.core.config import settings
from app.schemas.health import DatabaseHealth, HealthResponse


class HealthService:
    @staticmethod
    async def check_health(db: AsyncSession) -> HealthResponse:
        db_connected = False
        latency_ms = None
        pgvector_available = False
        db_error = None

        try:
            start_time = time.perf_counter()
            # Test connectivity
            await db.execute(text("SELECT 1"))
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            db_connected = True

            # Test pgvector extension presence
            result = await db.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            )
            extension_row = result.scalar_one_or_none()
            if extension_row == "vector":
                pgvector_available = True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            db_error = str(e)
            db_connected = False

        status = "healthy" if db_connected else "degraded"

        return HealthResponse(
            status=status,
            service=settings.PROJECT_NAME,
            version=settings.VERSION,
            environment=settings.ENVIRONMENT,
            tagline=settings.TAGLINE,
            database=DatabaseHealth(
                connected=db_connected,
                latency_ms=latency_ms,
                pgvector_available=pgvector_available,
                error=db_error,
            ),
        )
