from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.config import settings
from app.models.patient import Patient
from app.models.user import User
from app.schemas.auth import (
    AuthMeResponseData,
    LogoutResponseData,
    TokenResponseData,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.schemas.common import StandardResponse
from app.services.auth_service import AuthService

router = APIRouter()


def _set_auth_cookie(response: Response, token: str) -> None:
    """Set secure HttpOnly authentication cookie."""
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )


def _clear_auth_cookie(response: Response) -> None:
    """Clear authentication cookie upon logout."""
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/",
        domain=settings.COOKIE_DOMAIN,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )


@router.post(
    "/register",
    response_model=StandardResponse[TokenResponseData],
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Register a new user account with Argon2id password hashing and consent recording.",
)
async def register(
    payload: UserRegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[TokenResponseData]:
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent")

    user, access_token = await AuthService.register_user(
        db=db,
        register_data=payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    _set_auth_cookie(response, access_token)

    return StandardResponse(
        success=True,
        data=TokenResponseData(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.post(
    "/login",
    response_model=StandardResponse[TokenResponseData],
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate with email and password; sets HttpOnly cookie and returns JWT.",
)
async def login(
    payload: UserLoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[TokenResponseData]:
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent")

    user, access_token = await AuthService.authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    _set_auth_cookie(response, access_token)

    return StandardResponse(
        success=True,
        data=TokenResponseData(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.post(
    "/logout",
    response_model=StandardResponse[LogoutResponseData],
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Invalidate session and clear authentication cookie.",
)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[LogoutResponseData]:
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent")

    # Record logout audit log
    await AuthService.record_audit_log(
        db=db,
        user_id=current_user.id,
        action="USER_LOGOUT",
        resource_type="user",
        resource_id=str(current_user.id),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.commit()

    _clear_auth_cookie(response)

    return StandardResponse(
        success=True,
        data=LogoutResponseData(message="Successfully logged out"),
    )


@router.get(
    "/me",
    response_model=StandardResponse[AuthMeResponseData],
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Retrieve the currently authenticated user's profile and linked patient count.",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[AuthMeResponseData]:
    # Count patients linked to user
    res = await db.execute(
        select(func.count(Patient.id)).where(Patient.user_id == current_user.id)
    )
    patient_count = res.scalar() or 0

    return StandardResponse(
        success=True,
        data=AuthMeResponseData(
            user=UserResponse.model_validate(current_user),
            patient_count=patient_count,
        ),
    )
