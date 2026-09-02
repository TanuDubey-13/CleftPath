from datetime import date
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.voice import (
    PaginatedVoiceExercisesResponse,
    PaginatedVoiceSessionsResponse,
    VoiceExerciseResponse,
    VoiceOverviewResponse,
    VoiceSessionCreateRequest,
    VoiceSessionResponse,
    VoiceSessionUpdateRequest,
)
from app.services.voice_service import VoiceService

router = APIRouter()


# ============================================================================
# Voice Overview
# ============================================================================

@router.get(
    "/overview",
    response_model=StandardResponse[VoiceOverviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Voice Journey Overview",
    description="Retrieve practice activity metrics, total minutes, and non-diagnostic guidance.",
)
async def get_voice_overview(
    patient_id: Optional[uuid.UUID] = Query(default=None, description="Patient UUID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VoiceOverviewResponse]:
    overview = await VoiceService.get_voice_overview(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
    )
    return StandardResponse(success=True, data=overview)


# ============================================================================
# Voice Exercises
# ============================================================================

@router.get(
    "/exercises",
    response_model=StandardResponse[PaginatedVoiceExercisesResponse],
    status_code=status.HTTP_200_OK,
    summary="List Voice Exercises",
    description="Retrieve speech practice exercise library with optional stage and difficulty filters.",
)
async def list_voice_exercises(
    stage_id: Optional[int] = Query(default=None, description="Journey stage ID filter"),
    difficulty: Optional[str] = Query(default=None, description="Difficulty level (beginner, intermediate, advanced)"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedVoiceExercisesResponse]:
    exercises = await VoiceService.list_exercises(
        db=db,
        stage_id=stage_id,
        difficulty=difficulty,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=exercises)


@router.get(
    "/exercises/{exercise_id}",
    response_model=StandardResponse[VoiceExerciseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Voice Exercise Detail",
)
async def get_voice_exercise(
    exercise_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VoiceExerciseResponse]:
    exercise = await VoiceService.get_exercise_by_id(
        db=db,
        exercise_id=exercise_id,
    )
    return StandardResponse(success=True, data=exercise)


# ============================================================================
# Voice Sessions
# ============================================================================

@router.get(
    "/sessions",
    response_model=StandardResponse[PaginatedVoiceSessionsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Voice Sessions",
    description="Retrieve practice session history with date range and exercise filters.",
)
async def list_voice_sessions(
    patient_id: Optional[uuid.UUID] = Query(default=None, description="Patient UUID"),
    exercise_id: Optional[uuid.UUID] = Query(default=None, description="Filter by exercise UUID"),
    start_date: Optional[date] = Query(default=None, description="Start date filter"),
    end_date: Optional[date] = Query(default=None, description="End date filter"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedVoiceSessionsResponse]:
    sessions = await VoiceService.list_sessions(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
        exercise_id=exercise_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=sessions)


@router.get(
    "/sessions/{session_id}",
    response_model=StandardResponse[VoiceSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Voice Session Detail",
)
async def get_voice_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VoiceSessionResponse]:
    session = await VoiceService.get_session_by_id(
        db=db,
        session_id=session_id,
        current_user=current_user,
    )
    return StandardResponse(success=True, data=session)


@router.post(
    "/sessions",
    response_model=StandardResponse[VoiceSessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Voice Session",
    description="Log a completed voice practice session with duration, repetitions, and observations.",
)
async def create_voice_session(
    payload: VoiceSessionCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VoiceSessionResponse]:
    session = await VoiceService.create_session(
        db=db,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=session)


@router.patch(
    "/sessions/{session_id}",
    response_model=StandardResponse[VoiceSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Voice Session",
)
async def update_voice_session(
    session_id: uuid.UUID,
    payload: VoiceSessionUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VoiceSessionResponse]:
    session = await VoiceService.update_session(
        db=db,
        session_id=session_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=session)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Voice Session",
)
async def delete_voice_session(
    session_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await VoiceService.delete_session(
        db=db,
        session_id=session_id,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
