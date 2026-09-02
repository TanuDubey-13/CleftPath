import uuid
import pytest
from sqlalchemy import Column, Integer, String
from app.db.base import Base, TimestampMixin, UUIDMixin
from app.schemas.health import DatabaseHealth, HealthResponse
from app.services.health_service import HealthService


class SampleModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sample_test_model"
    name = Column(String(50), nullable=False)


def test_model_mixins():
    test_id = uuid.uuid4()
    instance = SampleModel(id=test_id, name="Test Record")
    assert instance.id == test_id
    assert instance.name == "Test Record"


@pytest.mark.asyncio
async def test_health_service_degraded_fallback():
    from unittest.mock import AsyncMock
    
    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("Connection refused to test DB")
    
    health = await HealthService.check_health(mock_db)
    assert health.status == "degraded"
    assert health.database.connected is False
    assert health.database.pgvector_available is False
    assert "Connection refused" in health.database.error
