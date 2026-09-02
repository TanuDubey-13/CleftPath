from datetime import datetime, timezone
from typing import Optional, Tuple
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    get_password_hash,
    validate_password_strength,
    verify_password,
)
from app.models.user import AuditLog, ConsentRecord, User
from app.schemas.auth import UserRegisterRequest


class AuthService:
    @staticmethod
    async def record_audit_log(
        db: AsyncSession,
        action: str,
        resource_type: str,
        user_id: Optional[uuid.UUID] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Create an immutable security and PHI access audit log entry."""
        audit = AuditLog(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address or "127.0.0.1",
            user_agent=user_agent or "CleftPathClient",
            created_at=datetime.now(timezone.utc),
        )
        db.add(audit)
        return audit

    @classmethod
    async def register_user(
        cls,
        db: AsyncSession,
        register_data: UserRegisterRequest,
        ip_address: str = "127.0.0.1",
        user_agent: Optional[str] = None,
    ) -> Tuple[User, str]:
        """Register a new user with Argon2id password hashing and consent recording."""
        normalized_email = register_data.email.strip().lower()

        # Check password strength
        validate_password_strength(register_data.password)

        # Check for duplicate email
        existing_res = await db.execute(select(User).where(User.email == normalized_email))
        if existing_res.scalar_one_or_none():
            raise AppException(
                message="An account with this email address already exists.",
                code="EMAIL_ALREADY_EXISTS",
                status_code=409,
                details=[{"field": "email", "issue": "Email is already registered."}],
            )

        # Hash password with Argon2id
        hashed_pw = get_password_hash(register_data.password)

        new_user = User(
            id=uuid.uuid4(),
            email=normalized_email,
            hashed_password=hashed_pw,
            first_name=register_data.first_name.strip(),
            last_name=register_data.last_name.strip(),
            role=register_data.role,
            is_active=True,
            is_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(new_user)
        await db.flush()

        # Record consent
        consent = ConsentRecord(
            id=uuid.uuid4(),
            user_id=new_user.id,
            terms_version="2026.1",
            privacy_version="2026.1",
            ai_safety_disclaimer_accepted=True,
            data_retention_accepted=True,
            ip_address=ip_address,
            consented_at=datetime.now(timezone.utc),
        )
        db.add(consent)

        # Record audit log
        await cls.record_audit_log(
            db=db,
            user_id=new_user.id,
            action="USER_REGISTERED",
            resource_type="user",
            resource_id=str(new_user.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        await db.commit()
        await db.refresh(new_user)

        # Generate JWT access token
        access_token = create_access_token(
            subject=new_user.id,
            role=new_user.role.value,
            email=new_user.email,
        )
        return new_user, access_token

    @classmethod
    async def authenticate_user(
        cls,
        db: AsyncSession,
        email: str,
        password: str,
        ip_address: str = "127.0.0.1",
        user_agent: Optional[str] = None,
    ) -> Tuple[User, str]:
        """Authenticate user with email/password and issue JWT access token."""
        normalized_email = email.strip().lower()

        res = await db.execute(select(User).where(User.email == normalized_email))
        user = res.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            # Avoid username enumeration by returning generic error
            raise AppException(
                message="Invalid email or password.",
                code="INVALID_CREDENTIALS",
                status_code=401,
            )

        if not user.is_active:
            raise AppException(
                message="Your account is inactive. Please contact support.",
                code="ACCOUNT_INACTIVE",
                status_code=403,
            )

        # Record login audit
        await cls.record_audit_log(
            db=db,
            user_id=user.id,
            action="USER_LOGIN",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        # Generate JWT access token
        access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
            email=user.email,
        )
        return user, access_token
