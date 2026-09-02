from typing import Callable, List, Optional
import uuid
from fastapi import Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.document import Document
from app.models.patient import Patient
from app.models.user import User, UserRole


def get_token_from_request(
    request: Request,
    authorization: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Extract JWT token from Authorization header or HttpOnly cookie."""
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1].strip()

    # Fallback to HttpOnly cookie
    cookie_token = request.cookies.get(settings.COOKIE_NAME)
    if cookie_token:
        return cookie_token.strip()

    return None


async def get_current_user(
    token: Optional[str] = Depends(get_token_from_request),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate token and retrieve current authenticated user from database."""
    if not token:
        raise AppException(
            message="Authentication credentials were not provided.",
            code="UNAUTHORIZED",
            status_code=401,
        )

    payload = decode_access_token(token)
    user_id_str = payload.get("sub")

    if not user_id_str:
        raise AppException(
            message="Invalid token payload.",
            code="UNAUTHORIZED",
            status_code=401,
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise AppException(
            message="Invalid user identifier in token.",
            code="UNAUTHORIZED",
            status_code=401,
        )

    res = await db.execute(select(User).where(User.id == user_uuid))
    user = res.scalar_one_or_none()

    if not user:
        raise AppException(
            message="User account no longer exists.",
            code="USER_NOT_FOUND",
            status_code=401,
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure that the authenticated user account is active."""
    if not current_user.is_active:
        raise AppException(
            message="User account is deactivated.",
            code="ACCOUNT_INACTIVE",
            status_code=403,
        )
    return current_user


def require_role(allowed_roles: List[UserRole]) -> Callable:
    """Role-based authorization dependency factory."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AppException(
                message="You do not have sufficient permissions to perform this action.",
                code="FORBIDDEN",
                status_code=403,
            )
        return current_user

    return role_checker


async def check_patient_ownership(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Patient:
    """Verify that the current user owns or is authorized to access the specified patient record."""
    res = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = res.scalar_one_or_none()

    if not patient:
        raise AppException(
            message="Patient record not found.",
            code="PATIENT_NOT_FOUND",
            status_code=404,
        )

    # Allow owner, clinician, or system admin
    if patient.user_id != current_user.id and current_user.role not in (
        UserRole.ADMIN,
        UserRole.CLINICIAN,
    ):
        raise AppException(
            message="Access to this patient record is forbidden.",
            code="FORBIDDEN",
            status_code=403,
        )

    return patient


async def check_document_ownership(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    """Verify that the current user owns the specified document."""
    res = await db.execute(select(Document).where(Document.id == document_id))
    document = res.scalar_one_or_none()

    if not document:
        raise AppException(
            message="Document not found.",
            code="DOCUMENT_NOT_FOUND",
            status_code=404,
        )

    if document.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise AppException(
            message="Access to this document is forbidden.",
            code="FORBIDDEN",
            status_code=403,
        )

    return document
