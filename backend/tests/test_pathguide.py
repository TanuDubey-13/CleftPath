"""
Comprehensive Unit and Integration Tests for Phase 10: PathGuide AI Chat & RAG Retrieval.
Verifies Authentication, IDOR thread/message isolation, Input bounds validation, RAG knowledge retrieval,
acute-symptom safety routing, output safety filters, audit logging, and sensitive data protection.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from httpx import ASGITransport, AsyncClient
import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.main import app
from app.models.knowledge import HealthArticle, KnowledgeChunk
from app.models.pathguide import PathGuideMessage, PathGuideThread
from app.models.user import User, UserRole
from app.schemas.pathguide import (
    PathGuideCitation,
    PathGuideMessageCreateRequest,
    PathGuideMessageResponse,
    PathGuideThreadCreateRequest,
    PathGuideThreadResponse,
    PathGuideThreadUpdateRequest,
)
from app.services.gemini_service import GeminiService
from app.services.pathguide_service import PathGuideService
from app.services.rag_service import RAGService


# ============================================================================
# 1. Authentication Tests (1 - 3)
# ============================================================================

@pytest.mark.asyncio
async def test_unauthenticated_threads_list_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/api/v1/pathguide/threads")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_thread_creation_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post("/api/v1/pathguide/threads", json={"title": "Test"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_message_creation_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post(f"/api/v1/pathguide/threads/{uuid.uuid4()}/messages", json={"content": "Hello"})
        assert res.status_code == 401


# ============================================================================
# 2. IDOR & Ownership Protection Tests (4 - 9)
# ============================================================================

@pytest.mark.asyncio
async def test_own_threads_list_accessible():
    user_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    thread = PathGuideThread(
        id=uuid.uuid4(),
        user_id=user_id,
        patient_id=None,
        title="Feeding Questions",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    thread.messages = []

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[thread])))),
    ]

    res = await PathGuideService.list_threads(mock_db, user)
    assert res.total == 1
    assert res.items[0].title == "Feeding Questions"


@pytest.mark.asyncio
async def test_cross_user_thread_detail_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    thread_a = PathGuideThread(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),  # Different user
        title="Secret Thread A",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    thread_a.messages = []

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread_a))

    with pytest.raises(AppException) as exc:
        await PathGuideService.get_thread_by_id(mock_db, thread_a.id, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_thread_update_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    thread_a = PathGuideThread(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Thread A",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread_a))

    with pytest.raises(AppException) as exc:
        await PathGuideService.update_thread(mock_db, thread_a.id, PathGuideThreadUpdateRequest(title="Renamed"), user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_thread_delete_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    thread_a = PathGuideThread(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Thread A",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread_a))

    with pytest.raises(AppException) as exc:
        await PathGuideService.delete_thread(mock_db, thread_a.id, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_messages_list_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    thread_a = PathGuideThread(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Thread A",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    thread_a.messages = []

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread_a))

    with pytest.raises(AppException) as exc:
        await PathGuideService.list_messages(mock_db, thread_a.id, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_message_creation_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    thread_a = PathGuideThread(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Thread A",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread_a))

    with pytest.raises(AppException) as exc:
        await PathGuideService.create_message(mock_db, thread_a.id, PathGuideMessageCreateRequest(content="Hi"), user_b)
    assert exc.value.status_code == 403


# ============================================================================
# 3. Input Validation Tests (10 - 13)
# ============================================================================

def test_empty_message_rejected():
    with pytest.raises(ValidationError):
        PathGuideMessageCreateRequest(content="")


def test_oversized_message_rejected():
    with pytest.raises(ValidationError):
        PathGuideMessageCreateRequest(content="A" * 4001)


@pytest.mark.asyncio
async def test_whitespace_only_message_rejected():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    thread = PathGuideThread(id=uuid.uuid4(), user_id=user.id, title="Thread", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread))

    with pytest.raises(AppException) as exc:
        await PathGuideService.create_message(mock_db, thread.id, PathGuideMessageCreateRequest(content="    \n   "), user)
    assert exc.value.status_code == 400
    assert exc.value.code == "INVALID_MESSAGE_CONTENT"


def test_invalid_thread_title_rejected():
    with pytest.raises(ValidationError):
        PathGuideThreadUpdateRequest(title="")


# ============================================================================
# 4. Suggested Prompts (14)
# ============================================================================

def test_suggested_prompts_returned():
    res = PathGuideService.get_suggested_prompts()
    assert len(res.prompts) >= 3
    assert all(p.category for p in res.prompts)
    assert all(p.prompt for p in res.prompts)


# ============================================================================
# 5. Thread Lifecycle Tests (15 - 17)
# ============================================================================

@pytest.mark.asyncio
async def test_thread_creation_and_retrieval():
    user_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    thread = PathGuideThread(
        id=uuid.uuid4(),
        user_id=user_id,
        patient_id=None,
        title="Bottle Preparation",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    thread.messages = []

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread))

    res = await PathGuideService.create_thread(mock_db, PathGuideThreadCreateRequest(title="Bottle Preparation"), user)
    assert res.title == "Bottle Preparation"
    assert res.user_id == user_id


@pytest.mark.asyncio
async def test_thread_update_title():
    user_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    thread = PathGuideThread(
        id=uuid.uuid4(),
        user_id=user_id,
        patient_id=None,
        title="Old Title",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    thread.messages = []

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread))

    res = await PathGuideService.update_thread(mock_db, thread.id, PathGuideThreadUpdateRequest(title="New Title"), user)
    assert thread.title == "New Title"


@pytest.mark.asyncio
async def test_thread_deletion_cascade():
    user_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    thread = PathGuideThread(
        id=uuid.uuid4(),
        user_id=user_id,
        title="To Delete",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread))

    await PathGuideService.delete_thread(mock_db, thread.id, user)
    mock_db.delete.assert_called_once_with(thread)


# ============================================================================
# 6. RAG, Safety & Message Generation Tests (18 - 22)
# ============================================================================

@pytest.mark.asyncio
async def test_rag_retrieval_and_message_generation():
    user_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    thread = PathGuideThread(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Care Conversation",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    article = HealthArticle(
        id=uuid.uuid4(),
        title="Understanding Specialized Cleft Feeders",
        slug="specialized-feeders",
        category="Feeding & Nutrition",
        summary="Clinical overview of Dr. Brown's and Haberman systems.",
        content_markdown="Unidirectional valve prevents milk regression.",
        author_source="ACPA",
        is_published=True,
    )
    chunk = KnowledgeChunk(
        id=uuid.uuid4(),
        article_id=article.id,
        chunk_index=0,
        content="Dr. Brown's specialty feeder uses a blue unidirectional valve insert.",
        embedding=RAGService.generate_synthetic_embedding("feeding"),
        created_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=thread)),  # thread lookup
        MagicMock(all=MagicMock(return_value=[(chunk, article)])),       # rag query
    ]

    payload = PathGuideMessageCreateRequest(content="How does Dr Brown specialty bottle work?")
    res = await PathGuideService.create_message(mock_db, thread.id, payload, user)

    assert res.role == "assistant"
    assert len(res.citations) >= 1
    assert res.citations[0].title == "Understanding Specialized Cleft Feeders"
    assert "cleft care team" in res.content.lower() or "cleftpath" in res.content.lower()


@pytest.mark.asyncio
def test_acute_symptoms_trigger_safety_routing():
    assert GeminiService.check_acute_symptoms("My baby is choking and cannot breathe!") is True
    assert GeminiService.check_acute_symptoms("There is heavy bleeding from the wound.") is True
    assert GeminiService.check_acute_symptoms("How do I wash the feeding bottle?") is False


def test_output_safety_filter_intercepts_diagnosis():
    unsafe_text = "Based on symptoms, I diagnose velopharyngeal insufficiency."
    safe_text = GeminiService.apply_output_safety_filter(unsafe_text)
    assert "I diagnose" not in safe_text
    assert "cannot diagnose medical conditions" in safe_text


@pytest.mark.asyncio
async def test_gemini_fallback_on_api_error():
    citations = [
        PathGuideCitation(
            title="Pre-Surgical Lip Taping Guidelines",
            category="NAM & Taping",
            summary="Skin preparation and tape application technique.",
        )
    ]
    response, flags, tokens = await GeminiService.generate_response(
        user_query="How to apply taping?",
        grounded_context="Context info",
        citations=citations,
    )
    assert len(response) > 20
    assert "Pre-Surgical Lip Taping Guidelines" in response
    assert flags["grounded_sources_count"] == 1


# ============================================================================
# 7. Audit Logging Tests (23 - 25)
# ============================================================================

@pytest.mark.asyncio
async def test_thread_creation_audit():
    user_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    thread = PathGuideThread(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Title",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    thread.messages = []

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread))

    await PathGuideService.create_thread(mock_db, PathGuideThreadCreateRequest(title="Title"), user, ip_address="127.0.0.1")
    assert mock_db.add.call_count >= 2  # thread + audit log


@pytest.mark.asyncio
async def test_message_creation_audit():
    user_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    thread = PathGuideThread(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Title",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=thread)),  # thread check
        MagicMock(all=MagicMock(return_value=[])),                       # vector query
        MagicMock(all=MagicMock(return_value=[])),                       # fallback query
    ]

    await PathGuideService.create_message(mock_db, thread.id, PathGuideMessageCreateRequest(content="Hello"), user, ip_address="127.0.0.1")
    assert mock_db.add.call_count >= 3  # user msg + assistant msg + audit log


@pytest.mark.asyncio
async def test_thread_deletion_audit():
    user_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    thread = PathGuideThread(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Title",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=thread))

    await PathGuideService.delete_thread(mock_db, thread.id, user, ip_address="127.0.0.1")
    mock_db.delete.assert_called_once_with(thread)
    assert mock_db.add.call_count >= 1  # audit log added


# ============================================================================
# 8. Sensitive Data Leakage Protection (26)
# ============================================================================

def test_sensitive_fields_not_leaked_in_pathguide_schemas():
    schemas = [
        PathGuideMessageResponse.model_json_schema(),
        PathGuideThreadResponse.model_json_schema(),
        PathGuideCitation.model_json_schema(),
    ]

    for s in schemas:
        schema_str = str(s).lower()
        assert "password" not in schema_str
        assert "jwt" not in schema_str
        assert "secret" not in schema_str
        assert "gemini_api_key" not in schema_str
