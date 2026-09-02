from datetime import date, datetime, time, timezone
import math
from typing import List, Optional
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppException
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.models.voice import VoiceExercise, VoiceSession
from app.schemas.voice import (
    PaginatedVoiceExercisesResponse,
    PaginatedVoiceSessionsResponse,
    VoiceExerciseResponse,
    VoiceOverviewResponse,
    VoiceSessionCreateRequest,
    VoiceSessionResponse,
    VoiceSessionUpdateRequest,
)
from app.services.auth_service import AuthService


class VoiceService:
    @classmethod
    async def get_patient_for_user(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
    ) -> Patient:
        """Resolve patient record with strict ownership and IDOR authorization check."""
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
                    message="Access to this patient's voice records is forbidden.",
                    code="FORBIDDEN",
                    status_code=403,
                )
            return patient

        # Default to first patient belonging to the current user
        res = await db.execute(
            select(Patient)
            .where(Patient.user_id == current_user.id)
            .order_by(Patient.created_at.asc())
        )
        patient = res.scalars().first()
        if not patient:
            raise AppException(
                message="No linked patient profile found for this user.",
                code="PATIENT_NOT_FOUND",
                status_code=404,
            )
        return patient

    # ========================================================================
    # 1. Voice Exercises
    # ========================================================================

    @classmethod
    async def list_exercises(
        cls,
        db: AsyncSession,
        stage_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedVoiceExercisesResponse:
        """List voice practice exercises with optional stage or difficulty filters."""
        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 100)

        filters = []
        if stage_id is not None:
            filters.append(VoiceExercise.stage_id == stage_id)
        if difficulty:
            filters.append(VoiceExercise.difficulty_level == difficulty.lower())

        count_query = select(func.count(VoiceExercise.id))
        if filters:
            count_query = count_query.where(*filters)
        count_res = await db.execute(count_query)
        total_items = count_res.scalar() or 0

        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        query = (
            select(VoiceExercise)
            .order_by(VoiceExercise.stage_id.asc().nulls_last(), VoiceExercise.title.asc())
            .offset(offset)
            .limit(safe_page_size)
        )
        if filters:
            query = query.where(*filters)

        res = await db.execute(query)
        rows = res.scalars().all()

        items = [VoiceExerciseResponse.model_validate(row) for row in rows]

        return PaginatedVoiceExercisesResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
        )

    @classmethod
    async def get_exercise_by_id(
        cls,
        db: AsyncSession,
        exercise_id: uuid.UUID,
    ) -> VoiceExerciseResponse:
        """Get details for a single voice exercise."""
        res = await db.execute(
            select(VoiceExercise).where(VoiceExercise.id == exercise_id)
        )
        exercise = res.scalar_one_or_none()

        if not exercise:
            raise AppException(
                message="Voice exercise not found.",
                code="EXERCISE_NOT_FOUND",
                status_code=404,
            )

        return VoiceExerciseResponse.model_validate(exercise)

    # ========================================================================
    # 2. Voice Sessions
    # ========================================================================

    @classmethod
    async def list_sessions(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
        exercise_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedVoiceSessionsResponse:
        """List voice practice sessions with ownership checks and filtering."""
        if start_date and end_date and start_date > end_date:
            raise AppException(
                message="start_date must be before or equal to end_date.",
                code="INVALID_DATE_RANGE",
                status_code=400,
            )

        patient = await cls.get_patient_for_user(db, current_user, patient_id)

        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 100)

        base_filters = [VoiceSession.patient_id == patient.id]
        if exercise_id:
            base_filters.append(VoiceSession.exercise_id == exercise_id)
        if start_date:
            start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
            base_filters.append(VoiceSession.recorded_at >= start_dt)
        if end_date:
            end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
            base_filters.append(VoiceSession.recorded_at <= end_dt)

        count_res = await db.execute(
            select(func.count(VoiceSession.id)).where(*base_filters)
        )
        total_items = count_res.scalar() or 0

        # Aggregated duration
        agg_res = await db.execute(
            select(func.coalesce(func.sum(VoiceSession.duration_seconds), 0)).where(
                VoiceSession.patient_id == patient.id
            )
        )
        total_seconds = agg_res.scalar() or 0
        total_minutes = math.ceil(total_seconds / 60)

        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        query = (
            select(VoiceSession)
            .where(*base_filters)
            .options(selectinload(VoiceSession.exercise))
            .order_by(VoiceSession.recorded_at.desc())
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(query)
        rows = res.scalars().all()

        items = [VoiceSessionResponse.model_validate(row) for row in rows]

        return PaginatedVoiceSessionsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
            total_practice_minutes=total_minutes,
            total_sessions_count=total_items,
        )

    @classmethod
    async def get_session_by_id(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        current_user: User,
    ) -> VoiceSessionResponse:
        """Get details of a single voice practice session with IDOR verification."""
        query = (
            select(VoiceSession)
            .where(VoiceSession.id == session_id)
            .options(selectinload(VoiceSession.patient), selectinload(VoiceSession.exercise))
        )
        res = await db.execute(query)
        session = res.scalar_one_or_none()

        if not session:
            raise AppException(
                message="Voice practice session not found.",
                code="SESSION_NOT_FOUND",
                status_code=404,
            )

        if session.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to this voice session is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        return VoiceSessionResponse.model_validate(session)

    @classmethod
    async def create_session(
        cls,
        db: AsyncSession,
        payload: VoiceSessionCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VoiceSessionResponse:
        """Create a new voice practice session record with audit logging."""
        patient = await cls.get_patient_for_user(db, current_user, payload.patient_id)

        # Validate exercise exists if provided
        if payload.exercise_id:
            ex_res = await db.execute(
                select(VoiceExercise).where(VoiceExercise.id == payload.exercise_id)
            )
            if not ex_res.scalar_one_or_none():
                raise AppException(
                    message="Referenced voice exercise not found.",
                    code="EXERCISE_NOT_FOUND",
                    status_code=404,
                )

        recorded_at = payload.recorded_at or datetime.now(timezone.utc)
        audio_key = payload.audio_s3_key or f"local_session/{uuid.uuid4()}"

        new_session = VoiceSession(
            id=uuid.uuid4(),
            patient_id=patient.id,
            exercise_id=payload.exercise_id,
            recorded_at=recorded_at,
            audio_s3_key=audio_key,
            duration_seconds=payload.duration_seconds,
            repetition_count=payload.repetition_count,
            dsp_features_json=payload.dsp_features_json or {},
            parent_notes=payload.parent_notes.strip() if payload.parent_notes else None,
            created_at=datetime.now(timezone.utc),
        )

        db.add(new_session)
        await db.flush()

        # Audit log
        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VOICE_SESSION_CREATED",
            resource_type="voice_session",
            resource_id=str(new_session.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_session_by_id(db, new_session.id, current_user)

    @classmethod
    async def update_session(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        payload: VoiceSessionUpdateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VoiceSessionResponse:
        """Update an existing voice practice session with IDOR verification."""
        query = (
            select(VoiceSession)
            .where(VoiceSession.id == session_id)
            .options(selectinload(VoiceSession.patient), selectinload(VoiceSession.exercise))
        )
        res = await db.execute(query)
        session = res.scalar_one_or_none()

        if not session:
            raise AppException(
                message="Voice practice session not found.",
                code="SESSION_NOT_FOUND",
                status_code=404,
            )

        if session.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to update this voice session is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        if payload.duration_seconds is not None:
            session.duration_seconds = payload.duration_seconds
        if payload.repetition_count is not None:
            session.repetition_count = payload.repetition_count
        if payload.parent_notes is not None:
            session.parent_notes = payload.parent_notes.strip() if payload.parent_notes else None

        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VOICE_SESSION_UPDATED",
            resource_type="voice_session",
            resource_id=str(session.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_session_by_id(db, session.id, current_user)

    @classmethod
    async def delete_session(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Delete a voice practice session with IDOR verification and audit logging."""
        query = (
            select(VoiceSession)
            .where(VoiceSession.id == session_id)
            .options(selectinload(VoiceSession.patient))
        )
        res = await db.execute(query)
        session = res.scalar_one_or_none()

        if not session:
            raise AppException(
                message="Voice practice session not found.",
                code="SESSION_NOT_FOUND",
                status_code=404,
            )

        if session.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to delete this voice session is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        await db.delete(session)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VOICE_SESSION_DELETED",
            resource_type="voice_session",
            resource_id=str(session_id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

    # ========================================================================
    # 3. Voice Overview Aggregation
    # ========================================================================

    @classmethod
    async def get_voice_overview(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
    ) -> VoiceOverviewResponse:
        """Compile practice activity summary and neutral educational guidance."""
        patient = await cls.get_patient_for_user(db, current_user, patient_id)

        # Total sessions & total seconds
        stats_res = await db.execute(
            select(
                func.count(VoiceSession.id),
                func.coalesce(func.sum(VoiceSession.duration_seconds), 0),
                func.count(func.distinct(VoiceSession.exercise_id)),
            ).where(VoiceSession.patient_id == patient.id)
        )
        total_sessions, total_seconds, unique_exercises = stats_res.one()
        total_minutes = math.ceil(total_seconds / 60)

        # Last session
        last_res = await db.execute(
            select(VoiceSession)
            .where(VoiceSession.patient_id == patient.id)
            .options(selectinload(VoiceSession.exercise))
            .order_by(VoiceSession.recorded_at.desc())
            .limit(1)
        )
        last_session = last_res.scalar_one_or_none()

        practice_guidance_notes = [
            "Use speech exploration exercises according to the instructions provided by your speech-language therapy team.",
            "Short, enjoyable daily practice sessions (2 to 5 minutes) support natural vocal play.",
            "Encourage eye contact, smiling, and positive reinforcement during sound imitation games.",
            "Keep an activity log to share observation notes during your routine SLP checkups.",
        ]

        return VoiceOverviewResponse(
            patient_id=patient.id,
            total_sessions_count=total_sessions,
            total_practice_minutes=total_minutes,
            unique_exercises_practiced=unique_exercises,
            last_session=VoiceSessionResponse.model_validate(last_session) if last_session else None,
            practice_guidance_notes=practice_guidance_notes,
        )
