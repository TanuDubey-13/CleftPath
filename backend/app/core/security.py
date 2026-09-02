from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AppException

# Argon2id password hashing context with recommended parameters
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=3,
    argon2__memory_cost=65536,  # 64 MB
    argon2__parallelism=4,
    argon2__salt_size=16,
    argon2__digest_size=32,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored Argon2id hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate secure Argon2id password hash."""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> None:
    """Validate password against CleftPath security policy (min 8 chars, mixed case, number, symbol)."""
    if len(password) < 8:
        raise AppException(
            message="Password must be at least 8 characters long.",
            code="WEAK_PASSWORD",
            status_code=400,
            details=[{"field": "password", "issue": "Minimum length is 8 characters."}],
        )
    if not any(c.isupper() for c in password):
        raise AppException(
            message="Password must contain at least one uppercase letter.",
            code="WEAK_PASSWORD",
            status_code=400,
            details=[{"field": "password", "issue": "Missing uppercase letter."}],
        )
    if not any(c.islower() for c in password):
        raise AppException(
            message="Password must contain at least one lowercase letter.",
            code="WEAK_PASSWORD",
            status_code=400,
            details=[{"field": "password", "issue": "Missing lowercase letter."}],
        )
    if not any(c.isdigit() for c in password):
        raise AppException(
            message="Password must contain at least one number.",
            code="WEAK_PASSWORD",
            status_code=400,
            details=[{"field": "password", "issue": "Missing digit."}],
        )


def create_access_token(
    subject: Union[str, uuid.UUID],
    role: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise AppException(
            message="Authentication token is invalid or expired.",
            code="UNAUTHORIZED",
            status_code=401,
            details=[{"issue": str(e)}],
        )
