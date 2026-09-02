from datetime import datetime, timezone
from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppException
from app.models.journey import JourneyMilestone, JourneyStage, MilestoneNote, MilestoneStatus
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.journey import (
    JourneyMilestoneResponse,
    JourneyOverviewResponse,
    JourneyPatientSummary,
    JourneyStageResponse,
    JourneySummaryResponse,
    MilestoneNoteCreateRequest,
    MilestoneNoteResponse,
    MilestoneUpdateRequest,
)
from app.services.auth_service import AuthService


class JourneyService:
    @staticmethod
    async def get_patient_for_user(
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
    ) -> Optional[Patient]:
        """Fetch primary or specified patient ensuring ownership/authorization."""
        if patient_id:
            res = await db.execute(select(Patient).where(Patient.id == patient_id))
            patient = res.scalar_one_or_none()
            if not patient:
                raise AppException(
                    message="Patient not found.",
                    code="PATIENT_NOT_FOUND",
                    status_code=404,
                )
            if patient.user_id != current_user.id and current_user.role not in (
                UserRole.ADMIN,
                UserRole.CLINICIAN,
            ):
                raise AppException(
                    message="Access to this patient journey is forbidden.",
                    code="FORBIDDEN",
                    status_code=403,
                )
            return patient

        # Default to first patient linked to user
        res = await db.execute(
            select(Patient)
            .where(Patient.user_id == current_user.id)
            .order_by(Patient.created_at.asc())
        )
        return res.scalars().first()

    @classmethod
    async def get_journey_overview(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
    ) -> JourneyOverviewResponse:
        """Fetch complete longitudinal roadmap with stages, milestones, and calculated progress."""
        patient = await cls.get_patient_for_user(db, current_user, patient_id)

        # Fetch all standard journey stages in ascending stage order
        stages_res = await db.execute(
            select(JourneyStage).order_by(JourneyStage.stage_number.asc())
        )
        stages = stages_res.scalars().all()

        if not patient:
            # User has no patient profile yet -> return empty journey overview
            empty_stages = [
                JourneyStageResponse(
                    id=stage.id,
                    stage_number=stage.stage_number,
                    title=stage.title,
                    age_range_label=stage.age_range_label,
                    description=stage.description,
                    color_hex=stage.color_hex,
                    status="upcoming",
                    milestones=[],
                    total_milestones=0,
                    completed_milestones=0,
                    progress_percentage=0.0,
                )
                for stage in stages
            ]
            return JourneyOverviewResponse(
                patient=None,
                stages=empty_stages,
                summary=JourneySummaryResponse(),
            )

        # Fetch patient's milestones with notes and author info
        milestones_res = await db.execute(
            select(JourneyMilestone)
            .where(JourneyMilestone.patient_id == patient.id)
            .options(
                selectinload(JourneyMilestone.notes).selectinload(MilestoneNote.user)
            )
            .order_by(JourneyMilestone.target_age_months.asc().nullslast())
        )
        all_patient_milestones = milestones_res.scalars().all()

        # Group milestones by stage_id
        milestones_by_stage: dict[int, list[JourneyMilestone]] = {}
        for m in all_patient_milestones:
            milestones_by_stage.setdefault(m.stage_id, []).append(m)

        total_milestones_count = len(all_patient_milestones)
        completed_count = 0
        in_progress_count = 0
        upcoming_count = 0

        stage_responses: List[JourneyStageResponse] = []
        current_active_stage_number: Optional[int] = None
        current_active_stage_title: Optional[str] = None

        for stage in stages:
            stage_milestones = milestones_by_stage.get(stage.id, [])
            total_stage_m = len(stage_milestones)
            completed_stage_m = sum(
                1 for m in stage_milestones if m.status == MilestoneStatus.COMPLETED
            )
            in_prog_stage_m = sum(
                1 for m in stage_milestones if m.status == MilestoneStatus.IN_PROGRESS
            )

            completed_count += completed_stage_m
            in_progress_count += in_prog_stage_m
            upcoming_count += sum(
                1 for m in stage_milestones if m.status == MilestoneStatus.UPCOMING
            )

            # Determine stage status
            if total_stage_m > 0 and completed_stage_m == total_stage_m:
                stage_status = "completed"
            elif in_prog_stage_m > 0 or (completed_stage_m > 0 and completed_stage_m < total_stage_m):
                stage_status = "in_progress"
            else:
                stage_status = "upcoming"

            if stage_status == "in_progress" and current_active_stage_number is None:
                current_active_stage_number = stage.stage_number
                current_active_stage_title = stage.title

            stage_pct = (
                round((completed_stage_m / total_stage_m) * 100, 1)
                if total_stage_m > 0
                else 0.0
            )

            m_responses: List[JourneyMilestoneResponse] = []
            for m in stage_milestones:
                note_responses = [
                    MilestoneNoteResponse(
                        id=n.id,
                        milestone_id=n.milestone_id,
                        user_id=n.user_id,
                        note_text=n.note_text,
                        photo_s3_key=n.photo_s3_key,
                        created_at=n.created_at,
                        author_name=f"{n.user.first_name} {n.user.last_name}" if n.user else "Caregiver",
                    )
                    for n in m.notes
                ]
                m_responses.append(
                    JourneyMilestoneResponse(
                        id=m.id,
                        patient_id=m.patient_id,
                        stage_id=m.stage_id,
                        title=m.title,
                        description=m.description,
                        target_age_months=m.target_age_months,
                        status=m.status,
                        is_custom=bool(m.is_custom),
                        target_date=m.target_date,
                        completed_at=m.completed_at,
                        notes_count=len(m.notes),
                        notes=note_responses,
                    )
                )

            stage_responses.append(
                JourneyStageResponse(
                    id=stage.id,
                    stage_number=stage.stage_number,
                    title=stage.title,
                    age_range_label=stage.age_range_label,
                    description=stage.description,
                    color_hex=stage.color_hex,
                    status=stage_status,
                    milestones=m_responses,
                    total_milestones=total_stage_m,
                    completed_milestones=completed_stage_m,
                    progress_percentage=stage_pct,
                )
            )

        # Fallback current active stage
        if current_active_stage_number is None and stages:
            current_active_stage_number = stages[0].stage_number
            current_active_stage_title = stages[0].title

        overall_pct = (
            round((completed_count / total_milestones_count) * 100, 1)
            if total_milestones_count > 0
            else 0.0
        )

        patient_summary = JourneyPatientSummary(
            id=patient.id,
            display_name=patient.display_name,
            date_of_birth=patient.date_of_birth,
            gender=patient.gender,
            cleft_lip=patient.cleft_lip.value,
            cleft_palate=patient.cleft_palate.value,
            cleft_alveolus=patient.cleft_alveolus.value,
        )

        summary = JourneySummaryResponse(
            total_milestones=total_milestones_count,
            completed_milestones=completed_count,
            in_progress_milestones=in_progress_count,
            upcoming_milestones=upcoming_count,
            overall_progress_percentage=overall_pct,
            current_stage_number=current_active_stage_number,
            current_stage_title=current_active_stage_title,
        )

        return JourneyOverviewResponse(
            patient=patient_summary,
            stages=stage_responses,
            summary=summary,
        )

    @classmethod
    async def get_all_stages(cls, db: AsyncSession) -> List[JourneyStage]:
        """List all reference clinical stages."""
        res = await db.execute(select(JourneyStage).order_by(JourneyStage.stage_number.asc()))
        return res.scalars().all()

    @classmethod
    async def get_milestone_by_id(
        cls,
        db: AsyncSession,
        milestone_id: uuid.UUID,
        current_user: User,
    ) -> JourneyMilestone:
        """Retrieve milestone details with strict ownership verification."""
        res = await db.execute(
            select(JourneyMilestone)
            .where(JourneyMilestone.id == milestone_id)
            .options(
                selectinload(JourneyMilestone.patient),
                selectinload(JourneyMilestone.notes).selectinload(MilestoneNote.user),
            )
        )
        milestone = res.scalar_one_or_none()
        if not milestone:
            raise AppException(
                message="Journey milestone not found.",
                code="MILESTONE_NOT_FOUND",
                status_code=404,
            )

        # IDOR check
        if milestone.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to this milestone is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        return milestone

    @classmethod
    async def update_milestone_status(
        cls,
        db: AsyncSession,
        milestone_id: uuid.UUID,
        update_data: MilestoneUpdateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> JourneyMilestone:
        """Update milestone status and completion timestamp with audit logging."""
        milestone = await cls.get_milestone_by_id(db, milestone_id, current_user)

        if update_data.status is not None:
            milestone.status = update_data.status
            if update_data.status == MilestoneStatus.COMPLETED:
                milestone.completed_at = update_data.completed_at or datetime.now(timezone.utc)
            elif update_data.status in (MilestoneStatus.UPCOMING, MilestoneStatus.IN_PROGRESS):
                milestone.completed_at = None

        if update_data.target_date is not None:
            milestone.target_date = update_data.target_date

        if update_data.completed_at is not None:
            milestone.completed_at = update_data.completed_at

        milestone.updated_at = datetime.now(timezone.utc)

        # Audit log
        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="MILESTONE_STATUS_UPDATED",
            resource_type="journey_milestone",
            resource_id=str(milestone.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        await db.commit()
        await db.refresh(milestone)
        return milestone

    @classmethod
    async def create_milestone_note(
        cls,
        db: AsyncSession,
        milestone_id: uuid.UUID,
        note_data: MilestoneNoteCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MilestoneNote:
        """Add a family memory or clinical note to an authorized milestone."""
        milestone = await cls.get_milestone_by_id(db, milestone_id, current_user)

        new_note = MilestoneNote(
            id=uuid.uuid4(),
            milestone_id=milestone.id,
            user_id=current_user.id,
            note_text=note_data.note_text.strip(),
            photo_s3_key=note_data.photo_s3_key,
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_note)

        # Audit log
        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="MILESTONE_NOTE_CREATED",
            resource_type="milestone_note",
            resource_id=str(new_note.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        await db.commit()
        await db.refresh(new_note)
        return new_note

    @classmethod
    async def get_milestone_notes(
        cls,
        db: AsyncSession,
        milestone_id: uuid.UUID,
        current_user: User,
    ) -> List[MilestoneNote]:
        """Fetch all notes for an authorized milestone."""
        milestone = await cls.get_milestone_by_id(db, milestone_id, current_user)
        res = await db.execute(
            select(MilestoneNote)
            .where(MilestoneNote.milestone_id == milestone.id)
            .options(selectinload(MilestoneNote.user))
            .order_by(MilestoneNote.created_at.desc())
        )
        return res.scalars().all()
