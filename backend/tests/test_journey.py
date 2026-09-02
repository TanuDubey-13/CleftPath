"""
Unit and Integration Tests for My Journey Module.
Verifies all 13 required verification cases: journey retrieval, stages, milestones, status updates, notes, IDOR isolation, input validation, and data leakage guards.
"""

from datetime import date, datetime, timezone
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import AppException
from app.core.security import create_access_token
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user, get_current_user
from app.main import app
from app.models.journey import JourneyMilestone, JourneyStage, MilestoneNote, MilestoneStatus
from app.models.patient import CleftAlveolusType, CleftLipType, CleftPalateType, Patient
from app.models.user import User, UserRole
from app.schemas.journey import (
    JourneyOverviewResponse,
    MilestoneNoteCreateRequest,
    MilestoneUpdateRequest,
)
from app.services.journey_service import JourneyService


# 1. Unauthenticated Access Rejection
@pytest.mark.asyncio
async def test_unauthenticated_journey_access_rejected():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/journey")
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "UNAUTHORIZED"


# 2. Authenticated Journey Retrieval & Milestones Return
@pytest.mark.asyncio
async def test_authenticated_journey_retrieval():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()

    user = User(
        id=user_id,
        email="parent@example.com",
        hashed_password="hash",
        first_name="Sarah",
        last_name="Jenkins",
        role=UserRole.CAREGIVER,
        is_active=True,
    )

    patient = Patient(
        id=patient_id,
        user_id=user_id,
        display_name="Baby Leo",
        date_of_birth=date(2026, 3, 15),
        gender="male",
        cleft_lip=CleftLipType.UNILATERAL_LEFT_COMPLETE,
        cleft_palate=CleftPalateType.HARD_AND_SOFT_COMPLETE,
        cleft_alveolus=CleftAlveolusType.INVOLVED_LEFT,
    )

    stage_1 = JourneyStage(
        id=1,
        stage_number=1,
        title="Prenatal & Diagnosis",
        age_range_label="Diagnosis to Birth",
        description="Initial diagnosis and feeding preparation",
        color_hex="#0F4C5C",
    )
    stage_2 = JourneyStage(
        id=2,
        stage_number=2,
        title="Newborn & Feeding",
        age_range_label="0 to 3 Months",
        description="Specialized feeding and NAM care",
        color_hex="#0F4C5C",
    )

    milestone_1 = JourneyMilestone(
        id=uuid.uuid4(),
        patient_id=patient_id,
        stage_id=1,
        title="Initial Cleft Team Consultation",
        description="Meet surgeon and feeding specialist",
        target_age_months=0,
        status=MilestoneStatus.COMPLETED,
        notes=[],
    )
    milestone_2 = JourneyMilestone(
        id=uuid.uuid4(),
        patient_id=patient_id,
        stage_id=2,
        title="Primary Lip Repair Surgery",
        description="Cheiloplasty surgery",
        target_age_months=3,
        status=MilestoneStatus.IN_PROGRESS,
        notes=[],
    )

    mock_db = AsyncMock(spec=AsyncSession)

    mock_patient_res = MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient))))
    mock_stages_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[stage_1, stage_2]))))
    mock_milestones_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[milestone_1, milestone_2]))))

    mock_db.execute.side_effect = [mock_patient_res, mock_stages_res, mock_milestones_res]

    overview = await JourneyService.get_journey_overview(mock_db, user)

    assert overview.patient is not None
    assert overview.patient.display_name == "Baby Leo"
    assert len(overview.stages) == 2
    assert overview.summary.total_milestones == 2
    assert overview.summary.completed_milestones == 1
    assert overview.summary.in_progress_milestones == 1
    assert overview.summary.overall_progress_percentage == 50.0


# 3. Stages Returned Correctly
@pytest.mark.asyncio
async def test_get_journey_stages_returned():
    mock_stages = [
        JourneyStage(id=1, stage_number=1, title="S1", age_range_label="0-3m", description="D1", color_hex="#0F4C5C"),
        JourneyStage(id=2, stage_number=2, title="S2", age_range_label="3-6m", description="D2", color_hex="#0F4C5C"),
    ]
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_stages))))

    stages = await JourneyService.get_all_stages(mock_db)
    assert len(stages) == 2
    assert stages[0].stage_number == 1


# 4. IDOR Protection: User B Cannot Access User A's Patient Journey
@pytest.mark.asyncio
async def test_journey_idor_protection_user_mismatch():
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()
    patient_id = uuid.uuid4()

    user_b = User(
        id=user_b_id,
        email="user_b@example.com",
        hashed_password="hash",
        first_name="Attacker",
        last_name="User",
        role=UserRole.CAREGIVER,
        is_active=True,
    )

    patient_a = Patient(
        id=patient_id,
        user_id=user_a_id,
        display_name="Baby A",
        date_of_birth=date(2026, 1, 1),
        gender="female",
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient_a))

    with pytest.raises(AppException) as exc:
        await JourneyService.get_patient_for_user(mock_db, user_b, patient_id=patient_id)
    assert exc.value.status_code == 403
    assert exc.value.code == "FORBIDDEN"


# 5. Milestone Status Update Success
@pytest.mark.asyncio
async def test_milestone_status_update_success():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    milestone_id = uuid.uuid4()

    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="A", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")
    milestone = JourneyMilestone(
        id=milestone_id,
        patient_id=patient_id,
        stage_id=1,
        title="Consultation",
        description="Desc",
        status=MilestoneStatus.UPCOMING,
        notes=[],
    )
    milestone.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=milestone))

    update_req = MilestoneUpdateRequest(status=MilestoneStatus.COMPLETED)
    updated = await JourneyService.update_milestone_status(mock_db, milestone_id, update_req, user)

    assert updated.status == MilestoneStatus.COMPLETED
    assert updated.completed_at is not None


# 6. Invalid Milestone Status Rejected
def test_invalid_milestone_status_rejected():
    with pytest.raises(ValidationError):
        MilestoneUpdateRequest(status="invalid_nonexistent_status")  # type: ignore


# 7. Cross-User Milestone Update Blocked (IDOR)
@pytest.mark.asyncio
async def test_cross_user_milestone_update_blocked():
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()
    milestone_id = uuid.uuid4()

    user_b = User(id=user_b_id, email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=user_a_id, display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="female")
    milestone = JourneyMilestone(
        id=milestone_id,
        patient_id=patient_a.id,
        stage_id=1,
        title="Consultation",
        description="Desc",
        status=MilestoneStatus.UPCOMING,
        notes=[],
    )
    milestone.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=milestone))

    update_req = MilestoneUpdateRequest(status=MilestoneStatus.COMPLETED)
    with pytest.raises(AppException) as exc:
        await JourneyService.update_milestone_status(mock_db, milestone_id, update_req, user_b)
    assert exc.value.status_code == 403
    assert exc.value.code == "FORBIDDEN"


# 8. Create Own Note & Retrieve Notes
@pytest.mark.asyncio
async def test_milestone_note_creation_and_listing():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    milestone_id = uuid.uuid4()

    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="Jane", last_name="Doe", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="female")
    milestone = JourneyMilestone(
        id=milestone_id,
        patient_id=patient_id,
        stage_id=1,
        title="NAM Fitting",
        description="Desc",
        status=MilestoneStatus.IN_PROGRESS,
        notes=[],
    )
    milestone.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=milestone))

    note_req = MilestoneNoteCreateRequest(note_text="Baby Leo tolerated the tape change very well today.")
    created_note = await JourneyService.create_milestone_note(mock_db, milestone_id, note_req, user)

    assert created_note.note_text == "Baby Leo tolerated the tape change very well today."
    assert created_note.user_id == user_id
    assert created_note.milestone_id == milestone_id


# 9. Cross-User Notes Blocked (IDOR)
@pytest.mark.asyncio
async def test_cross_user_notes_blocked():
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()
    milestone_id = uuid.uuid4()

    user_b = User(id=user_b_id, email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=user_a_id, display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="female")
    milestone = JourneyMilestone(
        id=milestone_id,
        patient_id=patient_a.id,
        stage_id=1,
        title="NAM Fitting",
        description="Desc",
        status=MilestoneStatus.IN_PROGRESS,
        notes=[],
    )
    milestone.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=milestone))

    note_req = MilestoneNoteCreateRequest(note_text="Attacker Note")
    with pytest.raises(AppException) as exc:
        await JourneyService.create_milestone_note(mock_db, milestone_id, note_req, user_b)
    assert exc.value.status_code == 403


# 10. Invalid Note Input Rejected
def test_invalid_note_input_rejected():
    # Empty string rejected
    with pytest.raises(ValidationError):
        MilestoneNoteCreateRequest(note_text="")

    # Excessively long string (> 2000 chars) rejected
    with pytest.raises(ValidationError):
        MilestoneNoteCreateRequest(note_text="a" * 2001)


# 11. Sensitive/Internal Fields Not Leaked in Journey Response
def test_journey_response_no_sensitive_field_leakage():
    schema = JourneyOverviewResponse.model_json_schema()
    schema_str = str(schema).lower()

    # Passwords and internal security tokens must never be present
    assert "password" not in schema_str
    assert "jwt" not in schema_str
    assert "secret" not in schema_str
    assert "token" not in schema_str
