from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.journey import (
    JourneyMilestoneResponse,
    JourneyOverviewResponse,
    JourneyStageResponse,
    MilestoneNoteCreateRequest,
    MilestoneNoteResponse,
    MilestoneUpdateRequest,
)
from app.services.journey_service import JourneyService

router = APIRouter()


@router.get(
    "",
    response_model=StandardResponse[JourneyOverviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get My Journey Roadmap",
    description="Retrieve the longitudinal care roadmap with stages, milestones, and calculated progress for the active patient.",
)
async def get_journey(
    patient_id: Optional[uuid.UUID] = Query(default=None, description="Optional specific patient UUID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[JourneyOverviewResponse]:
    overview = await JourneyService.get_journey_overview(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
    )
    return StandardResponse(success=True, data=overview)


@router.get(
    "/stages",
    response_model=StandardResponse[List[JourneyStageResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get Journey Stages",
    description="List all 8 ACPA standard longitudinal clinical stages.",
)
async def get_journey_stages(
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[JourneyStageResponse]]:
    stages = await JourneyService.get_all_stages(db=db)
    response_stages = [
        JourneyStageResponse(
            id=s.id,
            stage_number=s.stage_number,
            title=s.title,
            age_range_label=s.age_range_label,
            description=s.description,
            color_hex=s.color_hex,
            status="upcoming",
            milestones=[],
            total_milestones=0,
            completed_milestones=0,
            progress_percentage=0.0,
        )
        for s in stages
    ]
    return StandardResponse(success=True, data=response_stages)


@router.get(
    "/milestones/{milestone_id}",
    response_model=StandardResponse[JourneyMilestoneResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Milestone Details",
    description="Fetch a specific milestone's detailed description, status, target date, and notes.",
)
async def get_milestone_detail(
    milestone_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[JourneyMilestoneResponse]:
    milestone = await JourneyService.get_milestone_by_id(
        db=db,
        milestone_id=milestone_id,
        current_user=current_user,
    )
    notes_resp = [
        MilestoneNoteResponse(
            id=n.id,
            milestone_id=n.milestone_id,
            user_id=n.user_id,
            note_text=n.note_text,
            photo_s3_key=n.photo_s3_key,
            created_at=n.created_at,
            author_name=f"{n.user.first_name} {n.user.last_name}" if n.user else "Caregiver",
        )
        for n in milestone.notes
    ]
    return StandardResponse(
        success=True,
        data=JourneyMilestoneResponse(
            id=milestone.id,
            patient_id=milestone.patient_id,
            stage_id=milestone.stage_id,
            title=milestone.title,
            description=milestone.description,
            target_age_months=milestone.target_age_months,
            status=milestone.status,
            is_custom=milestone.is_custom,
            target_date=milestone.target_date,
            completed_at=milestone.completed_at,
            notes_count=len(milestone.notes),
            notes=notes_resp,
        ),
    )


@router.patch(
    "/milestones/{milestone_id}",
    response_model=StandardResponse[JourneyMilestoneResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Milestone Progress",
    description="Update milestone status (upcoming, in_progress, completed, skipped) or target dates.",
)
async def update_milestone_progress(
    milestone_id: uuid.UUID,
    payload: MilestoneUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[JourneyMilestoneResponse]:
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent")

    milestone = await JourneyService.update_milestone_status(
        db=db,
        milestone_id=milestone_id,
        update_data=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    notes_resp = [
        MilestoneNoteResponse(
            id=n.id,
            milestone_id=n.milestone_id,
            user_id=n.user_id,
            note_text=n.note_text,
            photo_s3_key=n.photo_s3_key,
            created_at=n.created_at,
            author_name=f"{n.user.first_name} {n.user.last_name}" if n.user else "Caregiver",
        )
        for n in milestone.notes
    ]

    return StandardResponse(
        success=True,
        data=JourneyMilestoneResponse(
            id=milestone.id,
            patient_id=milestone.patient_id,
            stage_id=milestone.stage_id,
            title=milestone.title,
            description=milestone.description,
            target_age_months=milestone.target_age_months,
            status=milestone.status,
            is_custom=milestone.is_custom,
            target_date=milestone.target_date,
            completed_at=milestone.completed_at,
            notes_count=len(milestone.notes),
            notes=notes_resp,
        ),
    )


@router.get(
    "/milestones/{milestone_id}/notes",
    response_model=StandardResponse[List[MilestoneNoteResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get Milestone Notes",
    description="List all private memories and clinical notes attached to an authorized milestone.",
)
async def get_milestone_notes(
    milestone_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[MilestoneNoteResponse]]:
    notes = await JourneyService.get_milestone_notes(
        db=db,
        milestone_id=milestone_id,
        current_user=current_user,
    )
    resp_notes = [
        MilestoneNoteResponse(
            id=n.id,
            milestone_id=n.milestone_id,
            user_id=n.user_id,
            note_text=n.note_text,
            photo_s3_key=n.photo_s3_key,
            created_at=n.created_at,
            author_name=f"{n.user.first_name} {n.user.last_name}" if n.user else "Caregiver",
        )
        for n in notes
    ]
    return StandardResponse(success=True, data=resp_notes)


@router.post(
    "/milestones/{milestone_id}/notes",
    response_model=StandardResponse[MilestoneNoteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Milestone Note",
    description="Attach a new private family note or clinical observation to an authorized milestone.",
)
async def add_milestone_note(
    milestone_id: uuid.UUID,
    payload: MilestoneNoteCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[MilestoneNoteResponse]:
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent")

    note = await JourneyService.create_milestone_note(
        db=db,
        milestone_id=milestone_id,
        note_data=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return StandardResponse(
        success=True,
        data=MilestoneNoteResponse(
            id=note.id,
            milestone_id=note.milestone_id,
            user_id=note.user_id,
            note_text=note.note_text,
            photo_s3_key=note.photo_s3_key,
            created_at=note.created_at,
            author_name=f"{current_user.first_name} {current_user.last_name}",
        ),
    )
