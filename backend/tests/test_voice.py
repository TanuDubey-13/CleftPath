"""
Comprehensive Unit and Integration Tests for Phase 9: Voice Journey Module.
Verifies Voice Exercises, Voice Sessions, strict IDOR patient isolation, input bounds validation, audit logging, and sensitive data protection.
"""

from datetime import date, datetime, timedelta, timezone
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import AppException
from app.main import app
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.models.voice import VoiceExercise, VoiceSession
from app.schemas.voice import (
    VoiceExerciseResponse,
    VoiceOverviewResponse,
    VoiceSessionCreateRequest,
    VoiceSessionResponse,
    VoiceSessionUpdateRequest,
)
from app.services.voice_service import VoiceService


# ============================================================================
# 1. Exercises Tests (1 - 5)
# ============================================================================

@pytest.mark.asyncio
async def test_list_voice_exercises_unauthenticated_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/api/v1/voice/exercises")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_list_voice_exercises_authenticated_success():
    ex = VoiceExercise(
        id=uuid.uuid4(),
        title="Bilabial Sound Exploration",
        target_phonemes=["p", "b", "m"],
        stage_id=2,
        prompt_text="Practice /pa/ and /ba/ sounds.",
        instructions="Maintain eye contact.",
        difficulty_level="beginner",
        created_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[ex])))),
    ]

    res = await VoiceService.list_exercises(mock_db, page=1, page_size=10)
    assert res.total == 1
    assert len(res.items) == 1
    assert res.items[0].title == "Bilabial Sound Exploration"
    assert res.items[0].target_phonemes == ["p", "b", "m"]


@pytest.mark.asyncio
async def test_get_voice_exercise_detail_success():
    ex_id = uuid.uuid4()
    ex = VoiceExercise(
        id=ex_id,
        title="Tongue-Tip Sounds",
        target_phonemes=["t", "d", "n"],
        stage_id=3,
        prompt_text="Practice /ta/ and /da/ sounds.",
        instructions="Encourage alveolar tap.",
        difficulty_level="intermediate",
        created_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=ex))

    res = await VoiceService.get_exercise_by_id(mock_db, ex_id)
    assert res.id == ex_id
    assert res.title == "Tongue-Tip Sounds"


@pytest.mark.asyncio
async def test_get_voice_exercise_nonexistent_returns_404():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    with pytest.raises(AppException) as exc:
        await VoiceService.get_exercise_by_id(mock_db, uuid.uuid4())
    assert exc.value.status_code == 404
    assert exc.value.code == "EXERCISE_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_voice_exercises_filter_by_stage_and_difficulty():
    ex = VoiceExercise(
        id=uuid.uuid4(),
        title="Vowel Prolongation",
        target_phonemes=["ah", "ee", "oo"],
        stage_id=2,
        prompt_text="Sustained vowel phonation.",
        instructions="Keep steady airflow.",
        difficulty_level="beginner",
        created_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[ex])))),
    ]

    res = await VoiceService.list_exercises(mock_db, stage_id=2, difficulty="beginner")
    assert res.total == 1
    assert res.items[0].difficulty_level == "beginner"


# ============================================================================
# 2. Session Authentication & IDOR Tests (6 - 13)
# ============================================================================

@pytest.mark.asyncio
async def test_unauthenticated_session_list_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/api/v1/voice/sessions")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_session_mutation_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post("/api/v1/voice/sessions", json={"duration_seconds": 60})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_own_session_records_accessible():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    session = VoiceSession(
        id=uuid.uuid4(),
        patient_id=patient_id,
        exercise_id=None,
        recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session",
        duration_seconds=90,
        repetition_count=3,
        dsp_features_json={},
        parent_notes="Practiced babble sounds",
        created_at=datetime.now(timezone.utc),
    )
    session.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalar=MagicMock(return_value=90)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[session])))),
    ]

    res = await VoiceService.list_sessions(mock_db, user)
    assert res.total == 1
    assert res.total_practice_minutes == 2
    assert res.items[0].duration_seconds == 90


@pytest.mark.asyncio
async def test_cross_user_session_list_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient_a))

    with pytest.raises(AppException) as exc:
        await VoiceService.get_patient_for_user(mock_db, user_b, patient_id=patient_a.id)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_session_detail_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    session = VoiceSession(
        id=uuid.uuid4(), patient_id=patient_a.id, recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session", duration_seconds=60, repetition_count=1,
        dsp_features_json={}, created_at=datetime.now(timezone.utc)
    )
    session.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=session))

    with pytest.raises(AppException) as exc:
        await VoiceService.get_session_by_id(mock_db, session.id, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_session_create_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient_a))

    payload = VoiceSessionCreateRequest(patient_id=patient_a.id, duration_seconds=60)
    with pytest.raises(AppException) as exc:
        await VoiceService.create_session(mock_db, payload, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_session_update_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    session = VoiceSession(
        id=uuid.uuid4(), patient_id=patient_a.id, recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session", duration_seconds=60, repetition_count=1,
        dsp_features_json={}, created_at=datetime.now(timezone.utc)
    )
    session.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=session))

    with pytest.raises(AppException) as exc:
        await VoiceService.update_session(mock_db, session.id, VoiceSessionUpdateRequest(duration_seconds=120), user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_session_delete_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    session = VoiceSession(
        id=uuid.uuid4(), patient_id=patient_a.id, recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session", duration_seconds=60, repetition_count=1,
        dsp_features_json={}, created_at=datetime.now(timezone.utc)
    )
    session.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=session))

    with pytest.raises(AppException) as exc:
        await VoiceService.delete_session(mock_db, session.id, user_b)
    assert exc.value.status_code == 403


# ============================================================================
# 3. Validation Tests (14 - 19)
# ============================================================================

def test_invalid_session_negative_duration_rejected():
    with pytest.raises(ValidationError):
        VoiceSessionCreateRequest(duration_seconds=-10)


def test_invalid_session_excessive_duration_rejected():
    with pytest.raises(ValidationError):
        VoiceSessionCreateRequest(duration_seconds=7200)  # max 3600s (1h)


def test_invalid_session_repetition_rejected():
    with pytest.raises(ValidationError):
        VoiceSessionCreateRequest(duration_seconds=30, repetition_count=0)


@pytest.mark.asyncio
async def test_invalid_date_range_rejected():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    mock_db = AsyncMock(spec=AsyncSession)
    with pytest.raises(AppException) as exc:
        await VoiceService.list_sessions(mock_db, user, start_date=date(2026, 5, 1), end_date=date(2026, 4, 1))
    assert exc.value.status_code == 400
    assert exc.value.code == "INVALID_DATE_RANGE"


@pytest.mark.asyncio
async def test_invalid_pagination_normalization():
    user_id = uuid.uuid4()
    patient = Patient(id=uuid.uuid4(), user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=5)),
        MagicMock(scalar=MagicMock(return_value=120)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]

    res = await VoiceService.list_sessions(mock_db, user, page=-5, page_size=500)
    assert res.page == 1
    assert res.page_size == 100


@pytest.mark.asyncio
async def test_referenced_nonexistent_exercise_rejected():
    user_id = uuid.uuid4()
    patient = Patient(id=uuid.uuid4(), user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # Exercise not found
    ]

    payload = VoiceSessionCreateRequest(exercise_id=uuid.uuid4(), duration_seconds=60)
    with pytest.raises(AppException) as exc:
        await VoiceService.create_session(mock_db, payload, user)
    assert exc.value.status_code == 404
    assert exc.value.code == "EXERCISE_NOT_FOUND"


# ============================================================================
# 4. Functionality & Lifecycle Tests (20 - 23)
# ============================================================================

@pytest.mark.asyncio
async def test_voice_session_creation():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    created = VoiceSession(
        id=uuid.uuid4(),
        patient_id=patient_id,
        exercise_id=None,
        recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session",
        duration_seconds=45,
        repetition_count=2,
        dsp_features_json={},
        parent_notes="Practiced sound games.",
        created_at=datetime.now(timezone.utc),
    )
    created.patient = patient
    created.exercise = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = VoiceSessionCreateRequest(duration_seconds=45, repetition_count=2, parent_notes="Practiced sound games.")
    res = await VoiceService.create_session(mock_db, payload, user)
    assert res.duration_seconds == 45
    assert res.repetition_count == 2


@pytest.mark.asyncio
async def test_voice_session_update():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    session = VoiceSession(
        id=uuid.uuid4(),
        patient_id=patient_id,
        exercise_id=None,
        recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session",
        duration_seconds=45,
        repetition_count=2,
        dsp_features_json={},
        parent_notes="Old note",
        created_at=datetime.now(timezone.utc),
    )
    session.patient = patient
    session.exercise = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=session))

    res = await VoiceService.update_session(mock_db, session.id, VoiceSessionUpdateRequest(duration_seconds=60, parent_notes="Updated note"), user)
    assert session.duration_seconds == 60
    assert session.parent_notes == "Updated note"


@pytest.mark.asyncio
async def test_voice_session_deletion():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    session = VoiceSession(
        id=uuid.uuid4(),
        patient_id=patient_id,
        exercise_id=None,
        recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session",
        duration_seconds=45,
        repetition_count=2,
        dsp_features_json={},
        created_at=datetime.now(timezone.utc),
    )
    session.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=session))

    await VoiceService.delete_session(mock_db, session.id, user)
    mock_db.delete.assert_called_once_with(session)


@pytest.mark.asyncio
async def test_voice_overview_aggregation():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    session = VoiceSession(
        id=uuid.uuid4(),
        patient_id=patient_id,
        exercise_id=None,
        recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session",
        duration_seconds=180,
        repetition_count=3,
        dsp_features_json={},
        created_at=datetime.now(timezone.utc),
    )
    session.exercise = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(one=MagicMock(return_value=(3, 360, 2))),  # total_sessions, total_seconds, unique_exercises
        MagicMock(scalar_one_or_none=MagicMock(return_value=session)),  # last session
    ]

    overview = await VoiceService.get_voice_overview(mock_db, user)
    assert overview.total_sessions_count == 3
    assert overview.total_practice_minutes == 6
    assert overview.unique_exercises_practiced == 2
    assert len(overview.practice_guidance_notes) > 0


# ============================================================================
# 5. Audit Logging Tests (24 - 26)
# ============================================================================

@pytest.mark.asyncio
async def test_voice_session_create_audit():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    created = VoiceSession(
        id=uuid.uuid4(),
        patient_id=patient_id,
        exercise_id=None,
        recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session",
        duration_seconds=30,
        repetition_count=1,
        dsp_features_json={},
        created_at=datetime.now(timezone.utc),
    )
    created.patient = patient
    created.exercise = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = VoiceSessionCreateRequest(duration_seconds=30)
    await VoiceService.create_session(mock_db, payload, user, ip_address="127.0.0.1")
    assert mock_db.add.call_count >= 2  # Added session + audit log


@pytest.mark.asyncio
async def test_voice_session_update_audit():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    session = VoiceSession(
        id=uuid.uuid4(),
        patient_id=patient_id,
        exercise_id=None,
        recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session",
        duration_seconds=30,
        repetition_count=1,
        dsp_features_json={},
        created_at=datetime.now(timezone.utc),
    )
    session.patient = patient
    session.exercise = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=session))

    await VoiceService.update_session(mock_db, session.id, VoiceSessionUpdateRequest(duration_seconds=45), user, ip_address="127.0.0.1")
    assert mock_db.add.call_count >= 1  # Added audit log


@pytest.mark.asyncio
async def test_voice_session_delete_audit():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    session = VoiceSession(
        id=uuid.uuid4(),
        patient_id=patient_id,
        exercise_id=None,
        recorded_at=datetime.now(timezone.utc),
        audio_s3_key="local_session",
        duration_seconds=30,
        repetition_count=1,
        dsp_features_json={},
        created_at=datetime.now(timezone.utc),
    )
    session.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=session))

    await VoiceService.delete_session(mock_db, session.id, user, ip_address="127.0.0.1")
    mock_db.delete.assert_called_once_with(session)
    assert mock_db.add.call_count >= 1  # Added audit log


# ============================================================================
# 6. Sensitive Data Leakage Test (27)
# ============================================================================

def test_sensitive_data_not_leaked_in_voice_schemas():
    schemas = [
        VoiceExerciseResponse.model_json_schema(),
        VoiceSessionResponse.model_json_schema(),
        VoiceOverviewResponse.model_json_schema(),
    ]

    for schema in schemas:
        schema_str = str(schema).lower()
        assert "password" not in schema_str
        assert "token" not in schema_str
        assert "jwt" not in schema_str
        assert "secret" not in schema_str
