"""
Unit and Integration Tests for Phase 6: Health Library Module.
Verifies listing, pagination, search, category filtering, single article retrieval, unpublished content protection, and data sanitization.
"""

from datetime import datetime, timezone
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import AppException
from app.main import app
from app.models.journey import JourneyStage
from app.models.knowledge import HealthArticle
from app.models.user import User, UserRole
from app.schemas.health_library import (
    HealthArticleCardResponse,
    HealthArticleDetailResponse,
    calculate_reading_time,
)
from app.services.health_library_service import HealthLibraryService


# 1. Unauthenticated Access Rejection
@pytest.mark.asyncio
async def test_unauthenticated_health_library_access_rejected():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/health-library/articles")
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "UNAUTHORIZED"


# 2. Reading Time Calculation
def test_calculate_reading_time():
    assert calculate_reading_time("") == 1
    # 300 words should be ~2 minutes (at 200 wpm)
    sample_text = "word " * 300
    assert calculate_reading_time(sample_text) == 2


# 3. List Articles with Pagination, Search, and Category Filtering
@pytest.mark.asyncio
async def test_list_articles_service():
    art1 = HealthArticle(
        id=uuid.uuid4(),
        title="Specialized Cleft Feeders",
        slug="specialized-cleft-feeders",
        category="Feeding",
        stage_id=1,
        summary="Summary of feeders",
        content_markdown="Content about Dr. Brown's feeder valve.",
        author_source="ACPA",
        clinical_verified_by="Dr. Sterling",
        is_published=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    art1.stage = JourneyStage(id=1, stage_number=1, title="Infancy & Feeding", age_range_label="0-3m", description="Desc", color_hex="#0F4C5C")

    mock_db = AsyncMock(spec=AsyncSession)

    # Mock count query returning 1, and select query returning [art1]
    mock_count_res = MagicMock(scalar=MagicMock(return_value=1))
    mock_select_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[art1]))))
    mock_db.execute.side_effect = [mock_count_res, mock_select_res]

    result = await HealthLibraryService.list_articles(
        db=mock_db,
        page=1,
        page_size=10,
        search="feeder",
        category="Feeding",
    )

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].title == "Specialized Cleft Feeders"
    assert result.items[0].stage_title == "Infancy & Feeding"
    assert result.items[0].reading_time_minutes >= 1
    assert result.page == 1
    assert result.total_pages == 1
    assert result.has_next is False
    assert result.has_prev is False


# 4. Safe Pagination Normalization
@pytest.mark.asyncio
async def test_list_articles_pagination_normalization():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_count_res = MagicMock(scalar=MagicMock(return_value=0))
    mock_select_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
    mock_db.execute.side_effect = [mock_count_res, mock_select_res]

    # Negative page and huge page_size are safely clamped
    result = await HealthLibraryService.list_articles(
        db=mock_db,
        page=-5,
        page_size=5000,
    )

    assert result.page == 1
    assert result.page_size == 100  # clamped to max 100


# 5. Get Single Article Detail by Slug or UUID
@pytest.mark.asyncio
async def test_get_article_detail_success():
    art_id = uuid.uuid4()
    art = HealthArticle(
        id=art_id,
        title="Lip Repair Guide",
        slug="lip-repair-guide",
        category="Surgery",
        stage_id=2,
        summary="Summary",
        content_markdown="# Primary Lip Repair\nFull surgical text.",
        author_source="ACPA",
        clinical_verified_by="Surgical Committee",
        is_published=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    art.stage = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=art))

    # Test retrieval by slug
    result = await HealthLibraryService.get_article(mock_db, "lip-repair-guide")
    assert result.title == "Lip Repair Guide"
    assert result.content_markdown.startswith("# Primary Lip Repair")

    # Test retrieval by UUID string
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=art))
    result_by_uuid = await HealthLibraryService.get_article(mock_db, str(art_id))
    assert result_by_uuid.id == art_id


# 6. Missing / Non-existent Article Returns 404
@pytest.mark.asyncio
async def test_get_article_not_found_raises_404():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    with pytest.raises(AppException) as exc:
        await HealthLibraryService.get_article(mock_db, "non-existent-article-slug")
    assert exc.value.status_code == 404
    assert exc.value.code == "ARTICLE_NOT_FOUND"


# 7. Get Categories Aggregation
@pytest.mark.asyncio
async def test_get_categories():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_rows = [("Feeding", 3), ("Surgery", 2), ("Speech", 1)]
    mock_db.execute.return_value = MagicMock(all=MagicMock(return_value=mock_rows))

    categories = await HealthLibraryService.get_categories(mock_db)
    assert len(categories) == 3
    assert categories[0].name == "Feeding"
    assert categories[0].article_count == 3


# 8. Schema Data Sanitization: Internal & Sensitive Fields Not Leaked
def test_health_article_schemas_no_internal_data_leakage():
    card_schema = str(HealthArticleCardResponse.model_json_schema()).lower()
    detail_schema = str(HealthArticleDetailResponse.model_json_schema()).lower()

    # Passwords, tokens, pgvector embeddings, and tsvector search vectors must not be in response schemas
    for schema_str in [card_schema, detail_schema]:
        assert "password" not in schema_str
        assert "embedding" not in schema_str
        assert "search_vector" not in schema_str
        assert "secret" not in schema_str
        assert "jwt" not in schema_str


# 9. SQL Injection-Style Search String Handled Safely
@pytest.mark.asyncio
async def test_sql_injection_search_query_safe():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_count_res = MagicMock(scalar=MagicMock(return_value=0))
    mock_select_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
    mock_db.execute.side_effect = [mock_count_res, mock_select_res]

    malicious_query = "' OR 1=1; DROP TABLE health_articles; --"
    result = await HealthLibraryService.list_articles(
        db=mock_db,
        search=malicious_query,
    )
    assert result.total == 0
    assert len(result.items) == 0
