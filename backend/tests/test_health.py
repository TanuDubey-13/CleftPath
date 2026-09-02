import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "CleftPath"
    assert data["tagline"] == "Every journey deserves a path forward."
    assert "database" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_api_v1_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "connected" in data["database"]
    assert "pgvector_available" in data["database"]


@pytest.mark.asyncio
async def test_openapi_docs_accessible(async_client: AsyncClient):
    response = await async_client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "CleftPath"
    assert "/health" in schema["paths"]
    assert "/api/v1/health" in schema["paths"]
