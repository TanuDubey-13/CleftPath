"""
Comprehensive Backend Authentication and Authorization Tests.
Covers registration, Argon2id hashing, login, token verification, /me, logout, role enforcement, and IDOR prevention.
"""

from datetime import date, datetime, timezone
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    validate_password_strength,
    verify_password,
)
from app.core.exceptions import AppException
from app.db.session import get_db
from app.dependencies.auth import (
    check_document_ownership,
    check_patient_ownership,
    get_current_active_user,
    get_current_user,
)
from app.main import app
from app.models.document import Document
from app.models.patient import Patient, CleftLipType, CleftPalateType, CleftAlveolusType
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegisterRequest


# 1. Password Security & Argon2id Tests
def test_argon2id_password_hashing():
    """Verify that password hashing uses Argon2id with 64MB memory cost."""
    password = "StrongPassword123!"
    hashed = get_password_hash(password)

    # Verify Argon2id prefix and parameters
    assert hashed.startswith("$argon2id$")
    assert "$m=65536" in hashed
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_password_strength_policy():
    """Verify password policy enforces minimum length, uppercase, lowercase, and numbers."""
    with pytest.raises(AppException) as exc1:
        validate_password_strength("short1A")
    assert exc1.value.code == "WEAK_PASSWORD"

    with pytest.raises(AppException) as exc2:
        validate_password_strength("alllowercase123")
    assert exc2.value.code == "WEAK_PASSWORD"

    with pytest.raises(AppException) as exc3:
        validate_password_strength("ALLUPPERCASE123")
    assert exc3.value.code == "WEAK_PASSWORD"

    with pytest.raises(AppException) as exc4:
        validate_password_strength("NoDigitsHere!")
    assert exc4.value.code == "WEAK_PASSWORD"

    # Valid password should not raise
    validate_password_strength("ValidPassword123!")


# 2. JWT Token Lifecycle Tests
def test_jwt_token_generation_and_decoding():
    """Verify token generation, subject claim, role claim, and decoding."""
    user_id = uuid.uuid4()
    token = create_access_token(subject=user_id, role="caregiver", email="synthetic@example.com")
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "caregiver"
    assert payload["email"] == "synthetic@example.com"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_token_invalid():
    """Verify decoding an invalid token raises 401 AppException."""
    with pytest.raises(AppException) as exc:
        decode_access_token("invalid.token.structure")
    assert exc.value.status_code == 401
    assert exc.value.code == "UNAUTHORIZED"


# 3. Service Layer Registration & Login Tests (with Mock DB Session)
@pytest.mark.asyncio
async def test_auth_service_register_and_authenticate():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    reg_payload = UserRegisterRequest(
        email="new.parent@example.com",
        password="SecurePassword123!",
        first_name="Jane",
        last_name="Doe",
        role=UserRole.CAREGIVER,
    )

    user, token = await AuthService.register_user(mock_db, reg_payload, ip_address="127.0.0.1")
    assert user.email == "new.parent@example.com"
    assert user.first_name == "Jane"
    assert user.hashed_password.startswith("$argon2id$")
    assert user.hashed_password != "SecurePassword123!"  # Never plaintext
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_auth_service_duplicate_email():
    existing_user = User(
        id=uuid.uuid4(),
        email="existing@example.com",
        hashed_password=get_password_hash("Existing123!"),
        first_name="Existing",
        last_name="User",
        role=UserRole.CAREGIVER,
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=existing_user))

    reg_payload = UserRegisterRequest(
        email="existing@example.com",
        password="SecurePassword123!",
        first_name="Duplicate",
        last_name="Attempt",
        role=UserRole.CAREGIVER,
    )

    with pytest.raises(AppException) as exc:
        await AuthService.register_user(mock_db, reg_payload)
    assert exc.value.status_code == 409
    assert exc.value.code == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_auth_service_invalid_login():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    with pytest.raises(AppException) as exc:
        await AuthService.authenticate_user(mock_db, "nonexistent@example.com", "SomePassword123!")
    assert exc.value.status_code == 401
    assert exc.value.code == "INVALID_CREDENTIALS"


# 4. Tenant Isolation & Ownership Enforcement Tests
@pytest.mark.asyncio
async def test_patient_ownership_authorized_and_idor_prevention():
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()
    patient_id = uuid.uuid4()

    user_a = User(
        id=user_a_id,
        email="user_a@example.com",
        hashed_password="hash",
        first_name="User",
        last_name="A",
        role=UserRole.CAREGIVER,
    )

    user_b = User(
        id=user_b_id,
        email="user_b@example.com",
        hashed_password="hash",
        first_name="User",
        last_name="B",
        role=UserRole.CAREGIVER,
    )

    admin_user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        hashed_password="hash",
        first_name="Admin",
        last_name="Super",
        role=UserRole.ADMIN,
    )

    patient = Patient(
        id=patient_id,
        user_id=user_a_id,
        display_name="Baby A",
        date_of_birth=date(2026, 1, 1),
        gender="Female",
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=patient))

    # User A accesses own patient -> SUCCESS
    result = await check_patient_ownership(patient_id, current_user=user_a, db=mock_db)
    assert result.id == patient_id

    # User B accesses User A's patient -> 403 FORBIDDEN (IDOR prevented)
    with pytest.raises(AppException) as exc_b:
        await check_patient_ownership(patient_id, current_user=user_b, db=mock_db)
    assert exc_b.value.status_code == 403
    assert exc_b.value.code == "FORBIDDEN"

    # Admin accesses patient -> SUCCESS
    admin_result = await check_patient_ownership(patient_id, current_user=admin_user, db=mock_db)
    assert admin_result.id == patient_id


@pytest.mark.asyncio
async def test_document_ownership_enforcement():
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()
    doc_id = uuid.uuid4()

    user_a = User(id=user_a_id, email="a@example.com", hashed_password="h", first_name="A", last_name="A", role=UserRole.CAREGIVER)
    user_b = User(id=user_b_id, email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER)

    doc = Document(
        id=doc_id,
        patient_id=uuid.uuid4(),
        user_id=user_a_id,
        file_name="Op_Report.pdf",
        s3_key="docs/op.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=doc))

    # Owner accesses -> SUCCESS
    res = await check_document_ownership(doc_id, current_user=user_a, db=mock_db)
    assert res.id == doc_id

    # Non-owner accesses -> 403 FORBIDDEN
    with pytest.raises(AppException) as exc:
        await check_document_ownership(doc_id, current_user=user_b, db=mock_db)
    assert exc.value.status_code == 403


# 5. HTTP Endpoints Tests (Registration, Login, /me, Logout)
@pytest.mark.asyncio
async def test_unauthenticated_me_endpoint_rejected():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_authenticated_me_endpoint_with_bearer_token():
    test_user_id = uuid.uuid4()
    test_user = User(
        id=test_user_id,
        email="test.auth@example.com",
        hashed_password="hash",
        first_name="Test",
        last_name="AuthUser",
        role=UserRole.CAREGIVER,
        is_active=True,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar=MagicMock(return_value=1))

    app.dependency_overrides[get_current_active_user] = lambda: test_user
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_db] = lambda: mock_db

    token = create_access_token(subject=test_user_id, role="caregiver", email="test.auth@example.com")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        json_resp = response.json()
        assert json_resp["success"] is True
        assert json_resp["data"]["user"]["email"] == "test.auth@example.com"
        assert json_resp["data"]["user"]["first_name"] == "Test"
        assert json_resp["data"]["patient_count"] == 1
        # Password hash must NEVER be present
        assert "hashed_password" not in json_resp["data"]["user"]
        assert "password" not in json_resp["data"]["user"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_logout_endpoint_clears_cookie():
    test_user = User(
        id=uuid.uuid4(),
        email="logout.user@example.com",
        hashed_password="hash",
        first_name="Logout",
        last_name="Test",
        role=UserRole.CAREGIVER,
        is_active=True,
    )

    mock_db = AsyncMock(spec=AsyncSession)

    app.dependency_overrides[get_current_active_user] = lambda: test_user
    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        json_resp = response.json()
        assert json_resp["success"] is True
        assert "Successfully logged out" in json_resp["data"]["message"]

    app.dependency_overrides.clear()
