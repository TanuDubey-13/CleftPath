from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.appointments import (
    AppointmentCreateRequest,
    AppointmentResponse,
    AppointmentStatus,
    AppointmentUpdateRequest,
    CareTeamMemberSummary,
    PaginatedAppointmentsResponse,
)
from app.schemas.common import StandardResponse
from app.services.appointment_service import AppointmentService

router = APIRouter()


@router.get(
    "",
    response_model=StandardResponse[PaginatedAppointmentsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Appointments",
    description="Retrieve user's patient appointments filtered by timeframe (upcoming, past, all) and status.",
)
async def list_appointments(
    patient_id: Optional[uuid.UUID] = Query(default=None, description="Patient UUID"),
    timeframe: str = Query(default="upcoming", description="Timeframe filter: upcoming, past, all"),
    status: Optional[AppointmentStatus] = Query(default=None, description="Filter by appointment status"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedAppointmentsResponse]:
    result = await AppointmentService.list_appointments(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
        timeframe=timeframe,
        status_filter=status,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=result)


@router.get(
    "/care-team",
    response_model=StandardResponse[List[CareTeamMemberSummary]],
    status_code=status.HTTP_200_OK,
    summary="List Care Team Specialists",
    description="Get linked care team multidisciplinary specialists for the user's patient.",
)
async def list_care_team_members(
    patient_id: Optional[uuid.UUID] = Query(default=None, description="Patient UUID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[CareTeamMemberSummary]]:
    members = await AppointmentService.list_care_team_members(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
    )
    return StandardResponse(success=True, data=members)


@router.get(
    "/{appointment_id}",
    response_model=StandardResponse[AppointmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Appointment Detail",
    description="Retrieve full clinical appointment details with IDOR verification.",
)
async def get_appointment(
    appointment_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[AppointmentResponse]:
    appointment = await AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=appointment_id,
        current_user=current_user,
    )
    return StandardResponse(success=True, data=appointment)


@router.post(
    "",
    response_model=StandardResponse[AppointmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Appointment",
    description="Create a new healthcare visit with doctor details, prep questions, and datetime.",
)
async def create_appointment(
    payload: AppointmentCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[AppointmentResponse]:
    appointment = await AppointmentService.create_appointment(
        db=db,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=appointment)


@router.patch(
    "/{appointment_id}",
    response_model=StandardResponse[AppointmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Appointment",
    description="Update appointment details or transition status with state-machine validation.",
)
async def update_appointment(
    appointment_id: uuid.UUID,
    payload: AppointmentUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[AppointmentResponse]:
    appointment = await AppointmentService.update_appointment(
        db=db,
        appointment_id=appointment_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=appointment)


@router.post(
    "/{appointment_id}/cancel",
    response_model=StandardResponse[AppointmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Cancel Appointment",
    description="Cancel a scheduled appointment safely with audit logging.",
)
async def cancel_appointment(
    appointment_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[AppointmentResponse]:
    appointment = await AppointmentService.cancel_appointment(
        db=db,
        appointment_id=appointment_id,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=appointment)
