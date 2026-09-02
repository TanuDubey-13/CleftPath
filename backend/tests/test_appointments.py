"""
Comprehensive Test Suite for Phase 7: Appointments Module.
Contains all 26 required verification cases for authentication, IDOR isolation, timeframe/status filters, pagination, validation, status state machine, audit logging, and care-team security.
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
from app.models.clinical import Appointment, CareTeamMember
from app.models.patient import Patient
from app.models.user import AuditLog, User, UserRole
from app.schemas.appointments import (
    AppointmentCreateRequest,
    AppointmentResponse,
    AppointmentStatus,
    AppointmentUpdateRequest,
)
from app.services.appointment_service import AppointmentService


# 1. Unauthenticated list blocked
@pytest.mark.asyncio
async def test_unauthenticated_list_blocked():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        res = await client.get("/api/v1/appointments")
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "UNAUTHORIZED"


# 2. Unauthenticated detail blocked
@pytest.mark.asyncio
async def test_unauthenticated_detail_blocked():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        res = await client.get(f"/api/v1/appointments/{uuid.uuid4()}")
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "UNAUTHORIZED"


# 3. Unauthenticated mutation blocked
@pytest.mark.asyncio
async def test_unauthenticated_mutation_blocked():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        res = await client.post("/api/v1/appointments", json={})
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "UNAUTHORIZED"


# 4. Own appointment list
@pytest.mark.asyncio
async def test_own_appointment_list():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="sarah@example.com", hashed_password="h", first_name="Sarah", last_name="J", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby Leo", date_of_birth=date(2026, 3, 15), gender="male")

    app1 = Appointment(
        id=uuid.uuid4(),
        patient_id=patient_id,
        specialist_name="Dr. Sterling",
        specialty="Cleft Surgeon",
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=10),
        duration_minutes=30,
        status="scheduled",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    app1.care_team_member = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalar=MagicMock(return_value=0)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=app1)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[app1])))),
    ]

    res = await AppointmentService.list_appointments(mock_db, user, timeframe="upcoming")
    assert res.total == 1
    assert res.items[0].specialist_name == "Dr. Sterling"


# 5. Cross-user list isolation
@pytest.mark.asyncio
async def test_cross_user_list_isolation():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient_a))

    with pytest.raises(AppException) as exc:
        await AppointmentService.get_patient_for_user(mock_db, user_b, patient_id=patient_a.id)
    assert exc.value.status_code == 403


# 6. Own appointment detail
@pytest.mark.asyncio
async def test_own_appointment_detail():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    app_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    app = Appointment(
        id=app_id, patient_id=patient_id, specialist_name="Dr. Chen", specialty="Orthodontist",
        scheduled_at=datetime.now(timezone.utc), duration_minutes=30, status="scheduled",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    app.patient = patient
    app.care_team_member = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=app))

    res = await AppointmentService.get_appointment_by_id(mock_db, app_id, user)
    assert res.id == app_id
    assert res.specialist_name == "Dr. Chen"


# 7. Cross-user detail blocked
@pytest.mark.asyncio
async def test_cross_user_detail_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    app = Appointment(
        id=uuid.uuid4(), patient_id=patient_a.id, specialist_name="Dr. Chen", specialty="Orthodontist",
        scheduled_at=datetime.now(timezone.utc), duration_minutes=30, status="scheduled",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    app.patient = patient_a
    app.care_team_member = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=app))

    with pytest.raises(AppException) as exc:
        await AppointmentService.get_appointment_by_id(mock_db, app.id, user_b)
    assert exc.value.status_code == 403


# 8. Missing appointment handled correctly (404)
@pytest.mark.asyncio
async def test_missing_appointment():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    with pytest.raises(AppException) as exc:
        await AppointmentService.get_appointment_by_id(mock_db, uuid.uuid4(), user)
    assert exc.value.status_code == 404
    assert exc.value.code == "APPOINTMENT_NOT_FOUND"


# 9. Upcoming filtering works
@pytest.mark.asyncio
async def test_upcoming_filtering():
    user_id = uuid.uuid4()
    patient = Patient(id=uuid.uuid4(), user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=2)),
        MagicMock(scalar=MagicMock(return_value=2)),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]

    res = await AppointmentService.list_appointments(mock_db, user, timeframe="upcoming")
    assert res.upcoming_count == 2


# 10. Past filtering works
@pytest.mark.asyncio
async def test_past_filtering():
    user_id = uuid.uuid4()
    patient = Patient(id=uuid.uuid4(), user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=3)),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalar=MagicMock(return_value=3)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]

    res = await AppointmentService.list_appointments(mock_db, user, timeframe="past")
    assert res.past_count == 3


# 11. Status filtering works
@pytest.mark.asyncio
async def test_status_filtering():
    user_id = uuid.uuid4()
    patient = Patient(id=uuid.uuid4(), user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalar=MagicMock(return_value=0)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]

    res = await AppointmentService.list_appointments(mock_db, user, status_filter=AppointmentStatus.CONFIRMED)
    assert res.total == 1


# 12. Pagination works
@pytest.mark.asyncio
async def test_pagination():
    user_id = uuid.uuid4()
    patient = Patient(id=uuid.uuid4(), user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=25)),
        MagicMock(scalar=MagicMock(return_value=15)),
        MagicMock(scalar=MagicMock(return_value=10)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]

    res = await AppointmentService.list_appointments(mock_db, user, page=2, page_size=10)
    assert res.page == 2
    assert res.total_pages == 3
    assert res.has_next is True
    assert res.has_prev is True


# 13. Invalid pagination safely normalized
@pytest.mark.asyncio
async def test_invalid_pagination():
    user_id = uuid.uuid4()
    patient = Patient(id=uuid.uuid4(), user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=5)),
        MagicMock(scalar=MagicMock(return_value=5)),
        MagicMock(scalar=MagicMock(return_value=0)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]

    res = await AppointmentService.list_appointments(mock_db, user, page=-5, page_size=999)
    assert res.page == 1
    assert res.page_size == 100


# 14. Invalid status rejected
def test_invalid_status():
    with pytest.raises(ValueError):
        AppointmentStatus("invalid_status_value")


# 15. Invalid date/time rejected
def test_invalid_datetime():
    with pytest.raises(ValidationError):
        AppointmentCreateRequest(
            specialist_name="Dr. Sterling",
            specialty="Surgery",
            scheduled_at="not-a-datetime",
        )


# 16. Cross-user creation blocked
@pytest.mark.asyncio
async def test_cross_user_creation_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient_a))

    payload = AppointmentCreateRequest(
        patient_id=patient_a.id,
        specialist_name="Dr. S",
        specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc),
    )

    with pytest.raises(AppException) as exc:
        await AppointmentService.create_appointment(mock_db, payload, user_b)
    assert exc.value.status_code == 403


# 17. Valid creation works
@pytest.mark.asyncio
async def test_valid_creation():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="p@example.com", hashed_password="h", first_name="P", last_name="P", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="female")

    created = Appointment(
        id=uuid.uuid4(), patient_id=patient_id, specialist_name="Dr. S", specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc), duration_minutes=30, status="scheduled",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    created.patient = patient
    created.care_team_member = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = AppointmentCreateRequest(
        specialist_name="Dr. S",
        specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc),
    )
    res = await AppointmentService.create_appointment(mock_db, payload, user)
    assert res.specialist_name == "Dr. S"
    assert res.status == AppointmentStatus.SCHEDULED


# 18. Cross-user update blocked
@pytest.mark.asyncio
async def test_cross_user_update_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    app = Appointment(
        id=uuid.uuid4(), patient_id=patient_a.id, specialist_name="Dr. S", specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc), duration_minutes=30, status="scheduled",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    app.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=app))

    with pytest.raises(AppException) as exc:
        await AppointmentService.update_appointment(mock_db, app.id, AppointmentUpdateRequest(specialist_name="New"), user_b)
    assert exc.value.status_code == 403


# 19. Valid update works
@pytest.mark.asyncio
async def test_valid_update():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    app = Appointment(
        id=uuid.uuid4(), patient_id=patient_id, specialist_name="Dr. S", specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc), duration_minutes=30, status="scheduled",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    app.patient = patient
    app.care_team_member = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=app))

    res = await AppointmentService.update_appointment(mock_db, app.id, AppointmentUpdateRequest(specialist_name="Dr. Updated"), user)
    assert app.specialist_name == "Dr. Updated"


# 20. Cross-user cancellation blocked
@pytest.mark.asyncio
async def test_cross_user_cancellation_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    app = Appointment(
        id=uuid.uuid4(), patient_id=patient_a.id, specialist_name="Dr. S", specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc), duration_minutes=30, status="scheduled",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    app.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=app))

    with pytest.raises(AppException) as exc:
        await AppointmentService.cancel_appointment(mock_db, app.id, user_b)
    assert exc.value.status_code == 403


# 21. Valid cancellation works
@pytest.mark.asyncio
async def test_valid_cancellation():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    app = Appointment(
        id=uuid.uuid4(), patient_id=patient_id, specialist_name="Dr. S", specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc), duration_minutes=30, status="scheduled",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    app.patient = patient
    app.care_team_member = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=app))

    await AppointmentService.cancel_appointment(mock_db, app.id, user)
    assert app.status == "cancelled"


# 22. Invalid status transitions rejected
@pytest.mark.asyncio
async def test_invalid_status_transition():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    # Completed appointment cannot move to scheduled
    completed_app = Appointment(
        id=uuid.uuid4(), patient_id=patient_id, specialist_name="Dr. S", specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc), duration_minutes=30, status="completed",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    completed_app.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=completed_app))

    with pytest.raises(AppException) as exc:
        await AppointmentService.update_appointment(mock_db, completed_app.id, AppointmentUpdateRequest(status=AppointmentStatus.SCHEDULED), user)
    assert exc.value.status_code == 400
    assert exc.value.code == "INVALID_STATUS_TRANSITION"


# 23. Sensitive fields not leaked
def test_sensitive_fields_not_leaked():
    schema = AppointmentResponse.model_json_schema()
    schema_str = str(schema).lower()

    assert "password" not in schema_str
    assert "token" not in schema_str
    assert "jwt" not in schema_str
    assert "secret" not in schema_str


# 24. Audit event created for mutation
@pytest.mark.asyncio
async def test_audit_event_created_for_mutation():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="p@example.com", hashed_password="h", first_name="P", last_name="P", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="female")

    created = Appointment(
        id=uuid.uuid4(), patient_id=patient_id, specialist_name="Dr. S", specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc), duration_minutes=30, status="scheduled",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    created.patient = patient
    created.care_team_member = None

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = AppointmentCreateRequest(
        specialist_name="Dr. S",
        specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc),
    )
    await AppointmentService.create_appointment(mock_db, payload, user, ip_address="127.0.0.1")
    # Verify db.add was called for Appointment and AuditLog
    assert mock_db.add.call_count >= 2


# 25. Care-team ownership isolation
@pytest.mark.asyncio
async def test_care_team_ownership_isolation():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient_a))

    with pytest.raises(AppException) as exc:
        await AppointmentService.list_care_team_members(mock_db, user_b, patient_id=patient_a.id)
    assert exc.value.status_code == 403


# 26. Invalid care-team member cannot be selected
@pytest.mark.asyncio
async def test_invalid_care_team_member_cannot_be_selected():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="female")

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # Care team member not found for patient
    ]

    payload = AppointmentCreateRequest(
        specialist_name="Dr. S",
        specialty="Surgery",
        scheduled_at=datetime.now(timezone.utc),
        care_team_member_id=uuid.uuid4(),
    )

    with pytest.raises(AppException) as exc:
        await AppointmentService.create_appointment(mock_db, payload, user)
    assert exc.value.status_code == 404
    assert exc.value.code == "CARE_TEAM_MEMBER_NOT_FOUND"
