from datetime import datetime, timezone
import math
from typing import List, Optional
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppException
from app.models.clinical import Appointment, CareTeamMember
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.appointments import (
    AppointmentCreateRequest,
    AppointmentResponse,
    AppointmentStatus,
    AppointmentUpdateRequest,
    CareTeamMemberSummary,
    PaginatedAppointmentsResponse,
)
from app.services.auth_service import AuthService


class AppointmentService:
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
                    message="Access to this patient's appointments is forbidden.",
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

    @classmethod
    async def list_appointments(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
        timeframe: str = "upcoming",  # 'upcoming', 'past', 'all'
        status_filter: Optional[AppointmentStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedAppointmentsResponse:
        """List appointments for user's patient with timeframe, status, and pagination."""
        patient = await cls.get_patient_for_user(db, current_user, patient_id)

        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 100)
        now_utc = datetime.now(timezone.utc)

        # Base filter by patient
        base_filters = [Appointment.patient_id == patient.id]

        # Timeframe filter
        timeframe_lower = (timeframe or "all").lower()
        if timeframe_lower == "upcoming":
            base_filters.append(Appointment.scheduled_at >= now_utc)
        elif timeframe_lower == "past":
            base_filters.append(Appointment.scheduled_at < now_utc)

        # Status filter
        if status_filter:
            base_filters.append(Appointment.status == status_filter.value)

        # Count total matching query
        count_res = await db.execute(
            select(func.count(Appointment.id)).where(*base_filters)
        )
        total_items = count_res.scalar() or 0

        # Count total upcoming and total past for summary cards
        upcoming_count_res = await db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.patient_id == patient.id,
                Appointment.scheduled_at >= now_utc,
                Appointment.status != AppointmentStatus.CANCELLED.value,
            )
        )
        upcoming_count = upcoming_count_res.scalar() or 0

        past_count_res = await db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.patient_id == patient.id,
                Appointment.scheduled_at < now_utc,
            )
        )
        past_count = past_count_res.scalar() or 0

        # Next upcoming appointment
        next_app_query = (
            select(Appointment)
            .where(
                Appointment.patient_id == patient.id,
                Appointment.scheduled_at >= now_utc,
                Appointment.status != AppointmentStatus.CANCELLED.value,
            )
            .options(selectinload(Appointment.care_team_member))
            .order_by(Appointment.scheduled_at.asc())
            .limit(1)
        )
        next_app_res = await db.execute(next_app_query)
        next_app_model = next_app_res.scalar_one_or_none()
        next_appointment_dto = (
            cls._map_appointment_dto(next_app_model) if next_app_model else None
        )

        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        # Order: upcoming -> asc, past -> desc, all -> desc
        order_clause = (
            Appointment.scheduled_at.asc()
            if timeframe_lower == "upcoming"
            else Appointment.scheduled_at.desc()
        )

        query = (
            select(Appointment)
            .where(*base_filters)
            .options(selectinload(Appointment.care_team_member))
            .order_by(order_clause)
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(query)
        rows = res.scalars().all()

        items = [cls._map_appointment_dto(app) for app in rows]

        return PaginatedAppointmentsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
            upcoming_count=upcoming_count,
            past_count=past_count,
            next_appointment=next_appointment_dto,
        )

    @classmethod
    async def get_appointment_by_id(
        cls,
        db: AsyncSession,
        appointment_id: uuid.UUID,
        current_user: User,
    ) -> AppointmentResponse:
        """Retrieve single appointment by ID with strict IDOR verification."""
        query = (
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.care_team_member),
            )
        )
        res = await db.execute(query)
        appointment = res.scalar_one_or_none()

        if not appointment:
            raise AppException(
                message="Appointment not found.",
                code="APPOINTMENT_NOT_FOUND",
                status_code=404,
            )

        # IDOR check
        if appointment.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to this appointment is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        return cls._map_appointment_dto(appointment)

    @classmethod
    async def create_appointment(
        cls,
        db: AsyncSession,
        payload: AppointmentCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AppointmentResponse:
        """Create new clinical appointment with ownership verification and audit logging."""
        patient = await cls.get_patient_for_user(db, current_user, payload.patient_id)

        # Validate care team member if provided
        if payload.care_team_member_id:
            ct_res = await db.execute(
                select(CareTeamMember).where(
                    CareTeamMember.id == payload.care_team_member_id,
                    CareTeamMember.patient_id == patient.id,
                )
            )
            if not ct_res.scalar_one_or_none():
                raise AppException(
                    message="Care team specialist not found for this patient.",
                    code="CARE_TEAM_MEMBER_NOT_FOUND",
                    status_code=404,
                )

        new_appointment = Appointment(
            id=uuid.uuid4(),
            patient_id=patient.id,
            care_team_member_id=payload.care_team_member_id,
            specialist_name=payload.specialist_name.strip(),
            specialty=payload.specialty.strip(),
            clinic_location=payload.clinic_location.strip() if payload.clinic_location else None,
            scheduled_at=payload.scheduled_at,
            duration_minutes=payload.duration_minutes,
            prep_questions=payload.prep_questions or [],
            summary_notes=payload.summary_notes.strip() if payload.summary_notes else None,
            status=AppointmentStatus.SCHEDULED.value,
        )

        db.add(new_appointment)
        await db.flush()

        # Audit log
        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="APPOINTMENT_CREATED",
            resource_type="appointment",
            resource_id=str(new_appointment.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        # Reload with relations
        return await cls.get_appointment_by_id(db, new_appointment.id, current_user)

    @classmethod
    async def update_appointment(
        cls,
        db: AsyncSession,
        appointment_id: uuid.UUID,
        payload: AppointmentUpdateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AppointmentResponse:
        """Update appointment with status transition validation, care-team verification, and audit logging."""
        query = (
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .options(selectinload(Appointment.patient))
        )
        res = await db.execute(query)
        appointment = res.scalar_one_or_none()

        if not appointment:
            raise AppException(
                message="Appointment not found.",
                code="APPOINTMENT_NOT_FOUND",
                status_code=404,
            )

        # IDOR check
        if appointment.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to update this appointment is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        # Validate status transitions
        if payload.status:
            current_status = appointment.status
            new_status = payload.status.value

            invalid_transitions = [
                # Cannot transition from CANCELLED (terminal state)
                (AppointmentStatus.CANCELLED.value, AppointmentStatus.SCHEDULED.value),
                (AppointmentStatus.CANCELLED.value, AppointmentStatus.CONFIRMED.value),
                (AppointmentStatus.CANCELLED.value, AppointmentStatus.COMPLETED.value),
                (AppointmentStatus.CANCELLED.value, AppointmentStatus.NO_SHOW.value),
                # Cannot transition from COMPLETED (terminal state)
                (AppointmentStatus.COMPLETED.value, AppointmentStatus.SCHEDULED.value),
                (AppointmentStatus.COMPLETED.value, AppointmentStatus.CONFIRMED.value),
                (AppointmentStatus.COMPLETED.value, AppointmentStatus.CANCELLED.value),
                (AppointmentStatus.COMPLETED.value, AppointmentStatus.NO_SHOW.value),
                # Cannot transition from NO_SHOW (terminal state)
                (AppointmentStatus.NO_SHOW.value, AppointmentStatus.SCHEDULED.value),
                (AppointmentStatus.NO_SHOW.value, AppointmentStatus.CONFIRMED.value),
                (AppointmentStatus.NO_SHOW.value, AppointmentStatus.COMPLETED.value),
                (AppointmentStatus.NO_SHOW.value, AppointmentStatus.CANCELLED.value),
            ]

            if (current_status, new_status) in invalid_transitions:
                raise AppException(
                    message=f"Cannot transition appointment status from '{current_status}' to '{new_status}'.",
                    code="INVALID_STATUS_TRANSITION",
                    status_code=400,
                )
            appointment.status = new_status

        # Validate care team member if updated
        if payload.care_team_member_id is not None:
            ct_res = await db.execute(
                select(CareTeamMember).where(
                    CareTeamMember.id == payload.care_team_member_id,
                    CareTeamMember.patient_id == appointment.patient_id,
                )
            )
            if not ct_res.scalar_one_or_none():
                raise AppException(
                    message="Care team specialist not found for this patient.",
                    code="CARE_TEAM_MEMBER_NOT_FOUND",
                    status_code=404,
                )
            appointment.care_team_member_id = payload.care_team_member_id

        if payload.specialist_name is not None:
            appointment.specialist_name = payload.specialist_name.strip()
        if payload.specialty is not None:
            appointment.specialty = payload.specialty.strip()
        if payload.clinic_location is not None:
            appointment.clinic_location = payload.clinic_location.strip()
        if payload.scheduled_at is not None:
            appointment.scheduled_at = payload.scheduled_at
        if payload.duration_minutes is not None:
            appointment.duration_minutes = payload.duration_minutes
        if payload.prep_questions is not None:
            appointment.prep_questions = payload.prep_questions
        if payload.summary_notes is not None:
            appointment.summary_notes = payload.summary_notes.strip()

        await db.flush()

        # Audit log
        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="APPOINTMENT_UPDATED",
            resource_type="appointment",
            resource_id=str(appointment.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_appointment_by_id(db, appointment.id, current_user)

    @classmethod
    async def cancel_appointment(
        cls,
        db: AsyncSession,
        appointment_id: uuid.UUID,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AppointmentResponse:
        """Cancel an appointment safely."""
        return await cls.update_appointment(
            db=db,
            appointment_id=appointment_id,
            payload=AppointmentUpdateRequest(status=AppointmentStatus.CANCELLED),
            current_user=current_user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @classmethod
    async def list_care_team_members(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
    ) -> List[CareTeamMemberSummary]:
        """List care team members for the user's patient."""
        patient = await cls.get_patient_for_user(db, current_user, patient_id)
        query = (
            select(CareTeamMember)
            .where(CareTeamMember.patient_id == patient.id)
            .order_by(CareTeamMember.specialist_name.asc())
        )
        res = await db.execute(query)
        rows = res.scalars().all()

        return [
            CareTeamMemberSummary(
                id=m.id,
                specialist_name=m.specialist_name,
                specialty=m.specialty,
                clinic_or_hospital=m.clinic_or_hospital,
                contact_phone=m.contact_phone,
                contact_email=m.contact_email,
            )
            for m in rows
        ]

    @staticmethod
    def _map_appointment_dto(app: Appointment) -> AppointmentResponse:
        return AppointmentResponse(
            id=app.id,
            patient_id=app.patient_id,
            care_team_member_id=app.care_team_member_id,
            specialist_name=app.specialist_name,
            specialty=app.specialty,
            clinic_location=app.clinic_location,
            scheduled_at=app.scheduled_at,
            duration_minutes=app.duration_minutes,
            prep_questions=app.prep_questions if isinstance(app.prep_questions, list) else [],
            summary_notes=app.summary_notes,
            status=AppointmentStatus(app.status),
            created_at=app.created_at,
            updated_at=app.updated_at,
            care_team_member=(
                CareTeamMemberSummary(
                    id=app.care_team_member.id,
                    specialist_name=app.care_team_member.specialist_name,
                    specialty=app.care_team_member.specialty,
                    clinic_or_hospital=app.care_team_member.clinic_or_hospital,
                    contact_phone=app.care_team_member.contact_phone,
                    contact_email=app.care_team_member.contact_email,
                )
                if app.care_team_member
                else None
            ),
        )
