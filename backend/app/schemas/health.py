from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    connected: bool
    latency_ms: Optional[float] = None
    pgvector_available: bool = False
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = Field(description="'healthy' or 'degraded'")
    service: str = "CleftPath API"
    version: str = "0.1.0"
    environment: str = "development"
    tagline: str = "Every journey deserves a path forward."
    database: DatabaseHealth
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
