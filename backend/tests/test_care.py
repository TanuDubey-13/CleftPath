"""
Comprehensive Unit and Integration Tests for Phase 8: Baby & Parent Care Module.
Verifies Feeding, Growth, NAM/Taping tracking, IDOR isolation, validation bounds, audit logging, and sensitive data protection.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import AppException
from app.main import app
from app.models.clinical import FeedingBottleType, FeedingLog, GrowthRecord, NAMTapingLog
from app.models.patient import Patient
from app.models.user import AuditLog, User, UserRole
from app.schemas.care import (
    CareOverviewResponse,
    FeedingLogCreateRequest,
    FeedingLogResponse,
    FeedingLogUpdateRequest,
    GrowthRecordCreateRequest,
    GrowthRecordResponse,
    GrowthRecordUpdateRequest,
    NAMTapingLogCreateRequest,
    NAMTapingLogResponse,
    NAMTapingLogUpdateRequest,
    RefluxSeverity,
)
from app.services.care_service import CareService


# ============================================================================
# Authentication Tests (1 - 4)
# ============================================================================

@pytest.mark.asyncio
async def test_unauthenticated_feeding_list_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/api/v1/care/feeding")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_feeding_mutation_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post("/api/v1/care/feeding", json={})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_growth_list_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/api/v1/care/growth")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_nam_list_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/api/v1/care/nam")
        assert res.status_code == 401


# ============================================================================
# Ownership & IDOR Tests (5 - 14)
# ============================================================================

@pytest.mark.asyncio
async def test_own_feeding_records_accessible():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    log = FeedingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("120.0"),
        duration_minutes=25, burping_breaks=2, reflux_severity="mild", created_at=datetime.now(timezone.utc)
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(one=MagicMock(return_value=(Decimal("120.0"), 1))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[log])))),
    ]

    res = await CareService.list_feeding_logs(mock_db, user)
    assert res.total == 1
    assert res.items[0].volume_ml == Decimal("120.0")


@pytest.mark.asyncio
async def test_cross_user_feeding_records_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient_a))

    with pytest.raises(AppException) as exc:
        await CareService.get_patient_for_user(mock_db, user_b, patient_id=patient_a.id)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_feeding_update_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")
    log = FeedingLog(
        id=uuid.uuid4(), patient_id=patient_a.id, logged_at=datetime.now(timezone.utc),
        bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("100"), duration_minutes=20,
        burping_breaks=1, reflux_severity="none", created_at=datetime.now(timezone.utc)
    )
    log.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=log))

    with pytest.raises(AppException) as exc:
        await CareService.update_feeding_log(mock_db, log.id, FeedingLogUpdateRequest(volume_ml=Decimal("150")), user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_feeding_delete_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")
    log = FeedingLog(
        id=uuid.uuid4(), patient_id=patient_a.id, logged_at=datetime.now(timezone.utc),
        bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("100"), duration_minutes=20,
        burping_breaks=1, reflux_severity="none", created_at=datetime.now(timezone.utc)
    )
    log.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=log))

    with pytest.raises(AppException) as exc:
        await CareService.delete_feeding_log(mock_db, log.id, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_own_growth_records_accessible():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    record = GrowthRecord(
        id=uuid.uuid4(), patient_id=patient_id, recorded_at=date(2026, 4, 1),
        weight_kg=Decimal("4.550"), height_cm=Decimal("55.2"), head_circumference_cm=Decimal("38.0"),
        created_at=datetime.now(timezone.utc)
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=Decimal("4.550"))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[record])))),
    ]

    res = await CareService.list_growth_records(mock_db, user)
    assert res.total == 1
    assert res.items[0].weight_kg == Decimal("4.550")


@pytest.mark.asyncio
async def test_cross_user_growth_records_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")
    record = GrowthRecord(
        id=uuid.uuid4(), patient_id=patient_a.id, recorded_at=date(2026, 4, 1), weight_kg=Decimal("4.5"),
        created_at=datetime.now(timezone.utc)
    )
    record.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=record))

    with pytest.raises(AppException) as exc:
        await CareService.get_growth_record_by_id(mock_db, record.id, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_growth_mutation_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient_a))

    payload = GrowthRecordCreateRequest(patient_id=patient_a.id, recorded_at=date(2026, 4, 1), weight_kg=Decimal("4.5"))
    with pytest.raises(AppException) as exc:
        await CareService.create_growth_record(mock_db, payload, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_own_nam_records_accessible():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    log = NAMTapingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        hours_worn=22, appliance_cleaned=True, tape_changed=True, skin_condition="normal",
        created_at=datetime.now(timezone.utc)
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalar=MagicMock(return_value=22)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[log])))),
    ]

    res = await CareService.list_nam_logs(mock_db, user)
    assert res.total == 1
    assert res.items[0].hours_worn == 22


@pytest.mark.asyncio
async def test_cross_user_nam_records_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")
    log = NAMTapingLog(
        id=uuid.uuid4(), patient_id=patient_a.id, logged_at=datetime.now(timezone.utc),
        hours_worn=20, appliance_cleaned=True, tape_changed=False, skin_condition="normal",
        created_at=datetime.now(timezone.utc)
    )
    log.patient = patient_a

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=log))

    with pytest.raises(AppException) as exc:
        await CareService.get_nam_log_by_id(mock_db, log.id, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_nam_mutation_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    patient_a = Patient(id=uuid.uuid4(), user_id=uuid.uuid4(), display_name="Baby A", date_of_birth=date(2026, 1, 1), gender="male")

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient_a))

    payload = NAMTapingLogCreateRequest(patient_id=patient_a.id, hours_worn=20)
    with pytest.raises(AppException) as exc:
        await CareService.create_nam_log(mock_db, payload, user_b)
    assert exc.value.status_code == 403


# ============================================================================
# Validation Tests (15 - 20)
# ============================================================================

def test_invalid_feeding_values_rejected():
    with pytest.raises(ValidationError):
        FeedingLogCreateRequest(
            bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY,
            volume_ml=Decimal("-10.0"),  # negative
            duration_minutes=20,
        )


def test_invalid_growth_values_rejected():
    with pytest.raises(ValidationError):
        GrowthRecordCreateRequest(
            recorded_at=date(2026, 4, 1),
            weight_kg=Decimal("0.1"),  # below min 0.5kg
        )


def test_invalid_nam_hours_rejected():
    with pytest.raises(ValidationError):
        NAMTapingLogCreateRequest(hours_worn=25)  # exceeds 24h


def test_invalid_dates_rejected():
    with pytest.raises(ValidationError):
        GrowthRecordCreateRequest(recorded_at="not-a-date", weight_kg=Decimal("4.0"))


@pytest.mark.asyncio
async def test_invalid_date_ranges_rejected():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    mock_db = AsyncMock(spec=AsyncSession)
    with pytest.raises(AppException) as exc:
        await CareService.list_feeding_logs(mock_db, user, start_date=date(2026, 5, 1), end_date=date(2026, 4, 1))
    assert exc.value.status_code == 400
    assert exc.value.code == "INVALID_DATE_RANGE"


@pytest.mark.asyncio
async def test_invalid_pagination_rejected():
    user_id = uuid.uuid4()
    patient = Patient(id=uuid.uuid4(), user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar=MagicMock(return_value=5)),
        MagicMock(one=MagicMock(return_value=(Decimal("0"), 0))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]

    res = await CareService.list_feeding_logs(mock_db, user, page=-1, page_size=200)
    assert res.page == 1
    assert res.page_size == 100


# ============================================================================
# Functionality Tests (21 - 30)
# ============================================================================

@pytest.mark.asyncio
async def test_feeding_creation():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    created = FeedingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("110.0"),
        duration_minutes=20, burping_breaks=1, reflux_severity="none", created_at=datetime.now(timezone.utc)
    )
    created.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = FeedingLogCreateRequest(bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("110.0"), duration_minutes=20)
    res = await CareService.create_feeding_log(mock_db, payload, user)
    assert res.volume_ml == Decimal("110.0")


@pytest.mark.asyncio
async def test_feeding_update():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    log = FeedingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("100.0"),
        duration_minutes=20, burping_breaks=1, reflux_severity="none", created_at=datetime.now(timezone.utc)
    )
    log.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=log))

    res = await CareService.update_feeding_log(mock_db, log.id, FeedingLogUpdateRequest(volume_ml=Decimal("130.0")), user)
    assert log.volume_ml == Decimal("130.0")


@pytest.mark.asyncio
async def test_feeding_deletion():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    log = FeedingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("100.0"),
        duration_minutes=20, burping_breaks=1, reflux_severity="none", created_at=datetime.now(timezone.utc)
    )
    log.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=log))

    await CareService.delete_feeding_log(mock_db, log.id, user)
    mock_db.delete.assert_called_once_with(log)


@pytest.mark.asyncio
async def test_growth_creation():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    created = GrowthRecord(
        id=uuid.uuid4(), patient_id=patient_id, recorded_at=date(2026, 4, 1), weight_kg=Decimal("4.800"),
        height_cm=Decimal("56.0"), head_circumference_cm=Decimal("38.5"), created_at=datetime.now(timezone.utc)
    )
    created.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = GrowthRecordCreateRequest(recorded_at=date(2026, 4, 1), weight_kg=Decimal("4.800"), height_cm=Decimal("56.0"))
    res = await CareService.create_growth_record(mock_db, payload, user)
    assert res.weight_kg == Decimal("4.800")


@pytest.mark.asyncio
async def test_growth_update():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    record = GrowthRecord(
        id=uuid.uuid4(), patient_id=patient_id, recorded_at=date(2026, 4, 1), weight_kg=Decimal("4.800"),
        created_at=datetime.now(timezone.utc)
    )
    record.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=record))

    await CareService.update_growth_record(mock_db, record.id, GrowthRecordUpdateRequest(weight_kg=Decimal("4.950")), user)
    assert record.weight_kg == Decimal("4.950")


@pytest.mark.asyncio
async def test_growth_deletion():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    record = GrowthRecord(
        id=uuid.uuid4(), patient_id=patient_id, recorded_at=date(2026, 4, 1), weight_kg=Decimal("4.800"),
        created_at=datetime.now(timezone.utc)
    )
    record.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=record))

    await CareService.delete_growth_record(mock_db, record.id, user)
    mock_db.delete.assert_called_once_with(record)


@pytest.mark.asyncio
async def test_nam_creation():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    created = NAMTapingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        hours_worn=23, appliance_cleaned=True, tape_changed=True, skin_condition="normal",
        created_at=datetime.now(timezone.utc)
    )
    created.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = NAMTapingLogCreateRequest(hours_worn=23, appliance_cleaned=True, tape_changed=True)
    res = await CareService.create_nam_log(mock_db, payload, user)
    assert res.hours_worn == 23


@pytest.mark.asyncio
async def test_nam_update():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    log = NAMTapingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        hours_worn=20, appliance_cleaned=True, tape_changed=False, skin_condition="normal",
        created_at=datetime.now(timezone.utc)
    )
    log.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=log))

    await CareService.update_nam_log(mock_db, log.id, NAMTapingLogUpdateRequest(hours_worn=22), user)
    assert log.hours_worn == 22


@pytest.mark.asyncio
async def test_nam_deletion():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    log = NAMTapingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        hours_worn=20, appliance_cleaned=True, tape_changed=False, skin_condition="normal",
        created_at=datetime.now(timezone.utc)
    )
    log.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=log))

    await CareService.delete_nam_log(mock_db, log.id, user)
    mock_db.delete.assert_called_once_with(log)


@pytest.mark.asyncio
async def test_overview_aggregation():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    feeding_log = FeedingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("120.0"),
        duration_minutes=25, burping_breaks=2, reflux_severity="none", created_at=datetime.now(timezone.utc)
    )
    growth_record = GrowthRecord(
        id=uuid.uuid4(), patient_id=patient_id, recorded_at=date(2026, 4, 1), weight_kg=Decimal("4.700"),
        created_at=datetime.now(timezone.utc)
    )
    nam_log = NAMTapingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        hours_worn=22, appliance_cleaned=True, tape_changed=True, skin_condition="normal",
        created_at=datetime.now(timezone.utc)
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(one=MagicMock(return_value=(Decimal("480.0"), 4))),  # feeding agg
        MagicMock(scalar_one_or_none=MagicMock(return_value=feeding_log)),  # last feeding
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[growth_record])))),  # growth rows
        MagicMock(scalar=MagicMock(return_value=22)),  # today nam hours
        MagicMock(scalar_one_or_none=MagicMock(return_value=nam_log)),  # last nam log
    ]

    overview = await CareService.get_care_overview(mock_db, user)
    assert overview.today_feeding_volume_ml == Decimal("480.0")
    assert overview.today_feeding_count == 4
    assert overview.today_nam_hours == 22
    assert len(overview.guidance_notes) > 0


# ============================================================================
# Audit Logging Tests (31 - 33)
# ============================================================================

@pytest.mark.asyncio
async def test_feeding_mutation_audit():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    created = FeedingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("110.0"),
        duration_minutes=20, burping_breaks=1, reflux_severity="none", created_at=datetime.now(timezone.utc)
    )
    created.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = FeedingLogCreateRequest(bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY, volume_ml=Decimal("110.0"), duration_minutes=20)
    await CareService.create_feeding_log(mock_db, payload, user, ip_address="127.0.0.1")
    assert mock_db.add.call_count >= 2


@pytest.mark.asyncio
async def test_growth_mutation_audit():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    created = GrowthRecord(
        id=uuid.uuid4(), patient_id=patient_id, recorded_at=date(2026, 4, 1), weight_kg=Decimal("4.800"),
        created_at=datetime.now(timezone.utc)
    )
    created.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = GrowthRecordCreateRequest(recorded_at=date(2026, 4, 1), weight_kg=Decimal("4.800"))
    await CareService.create_growth_record(mock_db, payload, user, ip_address="127.0.0.1")
    assert mock_db.add.call_count >= 2


@pytest.mark.asyncio
async def test_nam_mutation_audit():
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    user = User(id=user_id, email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    patient = Patient(id=patient_id, user_id=user_id, display_name="Baby", date_of_birth=date(2026, 1, 1), gender="male")

    created = NAMTapingLog(
        id=uuid.uuid4(), patient_id=patient_id, logged_at=datetime.now(timezone.utc),
        hours_worn=23, appliance_cleaned=True, tape_changed=True, skin_condition="normal",
        created_at=datetime.now(timezone.utc)
    )
    created.patient = patient

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=patient)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=created)),
    ]

    payload = NAMTapingLogCreateRequest(hours_worn=23)
    await CareService.create_nam_log(mock_db, payload, user, ip_address="127.0.0.1")
    assert mock_db.add.call_count >= 2


# ============================================================================
# Sensitive Data Leakage Test (34)
# ============================================================================

def test_sensitive_data_not_leaked():
    schemas = [
        FeedingLogResponse.model_json_schema(),
        GrowthRecordResponse.model_json_schema(),
        NAMTapingLogResponse.model_json_schema(),
        CareOverviewResponse.model_json_schema(),
    ]

    for schema in schemas:
        schema_str = str(schema).lower()
        assert "password" not in schema_str
        assert "token" not in schema_str
        assert "jwt" not in schema_str
        assert "secret" not in schema_str
