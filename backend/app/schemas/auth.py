from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class ConsentAgreementInput(BaseModel):
    terms_accepted: bool = Field(default=True, description="Accepted Terms of Service")
    privacy_policy_accepted: bool = Field(default=True, description="Accepted Privacy Policy")
    ai_safety_disclaimer_accepted: bool = Field(
        default=True, description="Acknowledged AI non-diagnostic medical disclaimer"
    )


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Strong password")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = Field(default=UserRole.CAREGIVER)
    consents: Optional[ConsentAgreementInput] = None

    model_config = ConfigDict(extra="forbid")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponseData(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthMeResponseData(BaseModel):
    user: UserResponse
    patient_count: int = 0


class LogoutResponseData(BaseModel):
    message: str = "Successfully logged out"
