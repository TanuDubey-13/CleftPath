from datetime import date, datetime, time, timezone
from decimal import Decimal
import math
from typing import List, Optional
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppException
from app.models.clinical import FeedingLog, GrowthRecord, NAMTapingLog
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.care import (
    CareOverviewResponse,
    FeedingLogCreateRequest,
    FeedingLogResponse,
    FeedingLogUpdateRequest,
    GrowthRecordCreateRequest,
    GrowthRecordResponse,
    GrowthRecordUpdateRequest,
    NAMTapingLogCreateRequest,
    NAMTapingLogResponse,
    NAMTapingLogUpdateRequest,
    PaginatedFeedingLogsResponse,
    PaginatedGrowthRecordsResponse,
    PaginatedNAMLogsResponse,
)
from app.services.auth_service import AuthService


class CareService:
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
                    message="Access to this patient's care records is forbidden.",
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
    # 1. Feeding Tracker Service
    # ========================================================================

    @classmethod
    async def list_feeding_logs(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedFeedingLogsResponse:
        """List feeding logs with date filters and pagination."""
        if start_date and end_date and start_date > end_date:
            raise AppException(
                message="start_date must be before or equal to end_date.",
                code="INVALID_DATE_RANGE",
                status_code=400,
            )

        patient = await cls.get_patient_for_user(db, current_user, patient_id)

        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 100)

        base_filters = [FeedingLog.patient_id == patient.id]
        if start_date:
            start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
            base_filters.append(FeedingLog.logged_at >= start_dt)
        if end_date:
            end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
            base_filters.append(FeedingLog.logged_at <= end_dt)

        # Count total items
        count_res = await db.execute(
            select(func.count(FeedingLog.id)).where(*base_filters)
        )
        total_items = count_res.scalar() or 0

        # Today's aggregates
        today_utc = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today_utc, time.min, tzinfo=timezone.utc)
        today_agg_res = await db.execute(
            select(
                func.coalesce(func.sum(FeedingLog.volume_ml), Decimal("0.0")),
                func.count(FeedingLog.id),
            ).where(
                FeedingLog.patient_id == patient.id,
                FeedingLog.logged_at >= today_start,
            )
        )
        today_volume, today_feeds = today_agg_res.one()

        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        query = (
            select(FeedingLog)
            .where(*base_filters)
            .order_by(FeedingLog.logged_at.desc())
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(query)
        rows = res.scalars().all()

        items = [FeedingLogResponse.model_validate(row) for row in rows]

        return PaginatedFeedingLogsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
            today_total_volume_ml=Decimal(str(today_volume)),
            today_total_feeds=today_feeds,
        )

    @classmethod
    async def get_feeding_log_by_id(
        cls,
        db: AsyncSession,
        log_id: uuid.UUID,
        current_user: User,
    ) -> FeedingLogResponse:
        """Get single feeding log with IDOR verification."""
        query = (
            select(FeedingLog)
            .where(FeedingLog.id == log_id)
            .options(selectinload(FeedingLog.patient))
        )
        res = await db.execute(query)
        log = res.scalar_one_or_none()

        if not log:
            raise AppException(
                message="Feeding log not found.",
                code="FEEDING_LOG_NOT_FOUND",
                status_code=404,
            )

        if log.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to this feeding log is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        return FeedingLogResponse.model_validate(log)

    @classmethod
    async def create_feeding_log(
        cls,
        db: AsyncSession,
        payload: FeedingLogCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> FeedingLogResponse:
        """Create a new feeding log with audit logging."""
        patient = await cls.get_patient_for_user(db, current_user, payload.patient_id)

        logged_at = payload.logged_at or datetime.now(timezone.utc)

        new_log = FeedingLog(
            id=uuid.uuid4(),
            patient_id=patient.id,
            logged_at=logged_at,
            bottle_type=payload.bottle_type,
            volume_ml=payload.volume_ml,
            duration_minutes=payload.duration_minutes,
            burping_breaks=payload.burping_breaks,
            reflux_severity=payload.reflux_severity.value,
            notes=payload.notes.strip() if payload.notes else None,
            created_at=datetime.now(timezone.utc),
        )

        db.add(new_log)
        await db.flush()

        # Audit log
        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="FEEDING_LOG_CREATED",
            resource_type="feeding_log",
            resource_id=str(new_log.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_feeding_log_by_id(db, new_log.id, current_user)

    @classmethod
    async def update_feeding_log(
        cls,
        db: AsyncSession,
        log_id: uuid.UUID,
        payload: FeedingLogUpdateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> FeedingLogResponse:
        """Update existing feeding log with IDOR verification and audit logging."""
        query = (
            select(FeedingLog)
            .where(FeedingLog.id == log_id)
            .options(selectinload(FeedingLog.patient))
        )
        res = await db.execute(query)
        log = res.scalar_one_or_none()

        if not log:
            raise AppException(
                message="Feeding log not found.",
                code="FEEDING_LOG_NOT_FOUND",
                status_code=404,
            )

        if log.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to update this feeding log is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        if payload.logged_at is not None:
            log.logged_at = payload.logged_at
        if payload.bottle_type is not None:
            log.bottle_type = payload.bottle_type
        if payload.volume_ml is not None:
            log.volume_ml = payload.volume_ml
        if payload.duration_minutes is not None:
            log.duration_minutes = payload.duration_minutes
        if payload.burping_breaks is not None:
            log.burping_breaks = payload.burping_breaks
        if payload.reflux_severity is not None:
            log.reflux_severity = payload.reflux_severity.value
        if payload.notes is not None:
            log.notes = payload.notes.strip() if payload.notes else None

        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="FEEDING_LOG_UPDATED",
            resource_type="feeding_log",
            resource_id=str(log.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_feeding_log_by_id(db, log.id, current_user)

    @classmethod
    async def delete_feeding_log(
        cls,
        db: AsyncSession,
        log_id: uuid.UUID,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Delete feeding log with IDOR verification and audit logging."""
        query = (
            select(FeedingLog)
            .where(FeedingLog.id == log_id)
            .options(selectinload(FeedingLog.patient))
        )
        res = await db.execute(query)
        log = res.scalar_one_or_none()

        if not log:
            raise AppException(
                message="Feeding log not found.",
                code="FEEDING_LOG_NOT_FOUND",
                status_code=404,
            )

        if log.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to delete this feeding log is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        await db.delete(log)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="FEEDING_LOG_DELETED",
            resource_type="feeding_log",
            resource_id=str(log_id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

    # ========================================================================
    # 2. Growth Records Service
    # ========================================================================

    @classmethod
    async def list_growth_records(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedGrowthRecordsResponse:
        """List growth records with date filtering and pagination."""
        if start_date and end_date and start_date > end_date:
            raise AppException(
                message="start_date must be before or equal to end_date.",
                code="INVALID_DATE_RANGE",
                status_code=400,
            )

        patient = await cls.get_patient_for_user(db, current_user, patient_id)

        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 100)

        base_filters = [GrowthRecord.patient_id == patient.id]
        if start_date:
            base_filters.append(GrowthRecord.recorded_at >= start_date)
        if end_date:
            base_filters.append(GrowthRecord.recorded_at <= end_date)

        count_res = await db.execute(
            select(func.count(GrowthRecord.id)).where(*base_filters)
        )
        total_items = count_res.scalar() or 0

        # Latest weight
        latest_res = await db.execute(
            select(GrowthRecord.weight_kg)
            .where(GrowthRecord.patient_id == patient.id)
            .order_by(GrowthRecord.recorded_at.desc(), GrowthRecord.created_at.desc())
            .limit(1)
        )
        latest_weight = latest_res.scalar_one_or_none()

        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        query = (
            select(GrowthRecord)
            .where(*base_filters)
            .order_by(GrowthRecord.recorded_at.desc(), GrowthRecord.created_at.desc())
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(query)
        rows = res.scalars().all()

        items = [GrowthRecordResponse.model_validate(row) for row in rows]

        return PaginatedGrowthRecordsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
            latest_weight_kg=latest_weight,
        )

    @classmethod
    async def get_growth_record_by_id(
        cls,
        db: AsyncSession,
        record_id: uuid.UUID,
        current_user: User,
    ) -> GrowthRecordResponse:
        """Get single growth record with IDOR verification."""
        query = (
            select(GrowthRecord)
            .where(GrowthRecord.id == record_id)
            .options(selectinload(GrowthRecord.patient))
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()

        if not record:
            raise AppException(
                message="Growth record not found.",
                code="GROWTH_RECORD_NOT_FOUND",
                status_code=404,
            )

        if record.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to this growth record is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        return GrowthRecordResponse.model_validate(record)

    @classmethod
    async def create_growth_record(
        cls,
        db: AsyncSession,
        payload: GrowthRecordCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> GrowthRecordResponse:
        """Create new growth record with audit logging."""
        patient = await cls.get_patient_for_user(db, current_user, payload.patient_id)

        new_record = GrowthRecord(
            id=uuid.uuid4(),
            patient_id=patient.id,
            recorded_at=payload.recorded_at,
            weight_kg=payload.weight_kg,
            height_cm=payload.height_cm,
            head_circumference_cm=payload.head_circumference_cm,
            weight_percentile=payload.weight_percentile,
            height_percentile=payload.height_percentile,
            created_at=datetime.now(timezone.utc),
        )

        db.add(new_record)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="GROWTH_RECORD_CREATED",
            resource_type="growth_record",
            resource_id=str(new_record.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_growth_record_by_id(db, new_record.id, current_user)

    @classmethod
    async def update_growth_record(
        cls,
        db: AsyncSession,
        record_id: uuid.UUID,
        payload: GrowthRecordUpdateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> GrowthRecordResponse:
        """Update growth record with IDOR verification and audit logging."""
        query = (
            select(GrowthRecord)
            .where(GrowthRecord.id == record_id)
            .options(selectinload(GrowthRecord.patient))
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()

        if not record:
            raise AppException(
                message="Growth record not found.",
                code="GROWTH_RECORD_NOT_FOUND",
                status_code=404,
            )

        if record.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to update this growth record is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        if payload.recorded_at is not None:
            record.recorded_at = payload.recorded_at
        if payload.weight_kg is not None:
            record.weight_kg = payload.weight_kg
        if payload.height_cm is not None:
            record.height_cm = payload.height_cm
        if payload.head_circumference_cm is not None:
            record.head_circumference_cm = payload.head_circumference_cm
        if payload.weight_percentile is not None:
            record.weight_percentile = payload.weight_percentile
        if payload.height_percentile is not None:
            record.height_percentile = payload.height_percentile

        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="GROWTH_RECORD_UPDATED",
            resource_type="growth_record",
            resource_id=str(record.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_growth_record_by_id(db, record.id, current_user)

    @classmethod
    async def delete_growth_record(
        cls,
        db: AsyncSession,
        record_id: uuid.UUID,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Delete growth record with IDOR verification and audit logging."""
        query = (
            select(GrowthRecord)
            .where(GrowthRecord.id == record_id)
            .options(selectinload(GrowthRecord.patient))
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()

        if not record:
            raise AppException(
                message="Growth record not found.",
                code="GROWTH_RECORD_NOT_FOUND",
                status_code=404,
            )

        if record.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to delete this growth record is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        await db.delete(record)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="GROWTH_RECORD_DELETED",
            resource_type="growth_record",
            resource_id=str(record_id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

    # ========================================================================
    # 3. NAM / Taping Tracker Service
    # ========================================================================

    @classmethod
    async def list_nam_logs(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedNAMLogsResponse:
        """List NAM / taping logs with date filters and pagination."""
        if start_date and end_date and start_date > end_date:
            raise AppException(
                message="start_date must be before or equal to end_date.",
                code="INVALID_DATE_RANGE",
                status_code=400,
            )

        patient = await cls.get_patient_for_user(db, current_user, patient_id)

        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 100)

        base_filters = [NAMTapingLog.patient_id == patient.id]
        if start_date:
            start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
            base_filters.append(NAMTapingLog.logged_at >= start_dt)
        if end_date:
            end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
            base_filters.append(NAMTapingLog.logged_at <= end_dt)

        count_res = await db.execute(
            select(func.count(NAMTapingLog.id)).where(*base_filters)
        )
        total_items = count_res.scalar() or 0

        # Today's hours worn
        today_utc = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today_utc, time.min, tzinfo=timezone.utc)
        today_hours_res = await db.execute(
            select(func.coalesce(func.sum(NAMTapingLog.hours_worn), 0)).where(
                NAMTapingLog.patient_id == patient.id,
                NAMTapingLog.logged_at >= today_start,
            )
        )
        today_hours = today_hours_res.scalar() or 0

        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        query = (
            select(NAMTapingLog)
            .where(*base_filters)
            .order_by(NAMTapingLog.logged_at.desc())
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(query)
        rows = res.scalars().all()

        items = [NAMTapingLogResponse.model_validate(row) for row in rows]

        return PaginatedNAMLogsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
            today_hours_worn=min(today_hours, 24),
        )

    @classmethod
    async def get_nam_log_by_id(
        cls,
        db: AsyncSession,
        log_id: uuid.UUID,
        current_user: User,
    ) -> NAMTapingLogResponse:
        """Get single NAM log with IDOR verification."""
        query = (
            select(NAMTapingLog)
            .where(NAMTapingLog.id == log_id)
            .options(selectinload(NAMTapingLog.patient))
        )
        res = await db.execute(query)
        log = res.scalar_one_or_none()

        if not log:
            raise AppException(
                message="NAM log not found.",
                code="NAM_LOG_NOT_FOUND",
                status_code=404,
            )

        if log.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to this NAM log is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        return NAMTapingLogResponse.model_validate(log)

    @classmethod
    async def create_nam_log(
        cls,
        db: AsyncSession,
        payload: NAMTapingLogCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> NAMTapingLogResponse:
        """Create new NAM log with audit logging."""
        patient = await cls.get_patient_for_user(db, current_user, payload.patient_id)

        logged_at = payload.logged_at or datetime.now(timezone.utc)

        new_log = NAMTapingLog(
            id=uuid.uuid4(),
            patient_id=patient.id,
            logged_at=logged_at,
            hours_worn=payload.hours_worn,
            appliance_cleaned=payload.appliance_cleaned,
            tape_changed=payload.tape_changed,
            skin_condition=payload.skin_condition.strip(),
            notes=payload.notes.strip() if payload.notes else None,
            created_at=datetime.now(timezone.utc),
        )

        db.add(new_log)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="NAM_TAPING_LOG_CREATED",
            resource_type="nam_taping_log",
            resource_id=str(new_log.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_nam_log_by_id(db, new_log.id, current_user)

    @classmethod
    async def update_nam_log(
        cls,
        db: AsyncSession,
        log_id: uuid.UUID,
        payload: NAMTapingLogUpdateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> NAMTapingLogResponse:
        """Update NAM log with IDOR verification and audit logging."""
        query = (
            select(NAMTapingLog)
            .where(NAMTapingLog.id == log_id)
            .options(selectinload(NAMTapingLog.patient))
        )
        res = await db.execute(query)
        log = res.scalar_one_or_none()

        if not log:
            raise AppException(
                message="NAM log not found.",
                code="NAM_LOG_NOT_FOUND",
                status_code=404,
            )

        if log.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to update this NAM log is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        if payload.logged_at is not None:
            log.logged_at = payload.logged_at
        if payload.hours_worn is not None:
            log.hours_worn = payload.hours_worn
        if payload.appliance_cleaned is not None:
            log.appliance_cleaned = payload.appliance_cleaned
        if payload.tape_changed is not None:
            log.tape_changed = payload.tape_changed
        if payload.skin_condition is not None:
            log.skin_condition = payload.skin_condition.strip()
        if payload.notes is not None:
            log.notes = payload.notes.strip() if payload.notes else None

        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="NAM_TAPING_LOG_UPDATED",
            resource_type="nam_taping_log",
            resource_id=str(log.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_nam_log_by_id(db, log.id, current_user)

    @classmethod
    async def delete_nam_log(
        cls,
        db: AsyncSession,
        log_id: uuid.UUID,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Delete NAM log with IDOR verification and audit logging."""
        query = (
            select(NAMTapingLog)
            .where(NAMTapingLog.id == log_id)
            .options(selectinload(NAMTapingLog.patient))
        )
        res = await db.execute(query)
        log = res.scalar_one_or_none()

        if not log:
            raise AppException(
                message="NAM log not found.",
                code="NAM_LOG_NOT_FOUND",
                status_code=404,
            )

        if log.patient.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to delete this NAM log is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        await db.delete(log)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="NAM_TAPING_LOG_DELETED",
            resource_type="nam_taping_log",
            resource_id=str(log_id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

    # ========================================================================
    # 4. Care Overview Aggregation
    # ========================================================================

    @classmethod
    async def get_care_overview(
        cls,
        db: AsyncSession,
        current_user: User,
        patient_id: Optional[uuid.UUID] = None,
    ) -> CareOverviewResponse:
        """Aggregate care metrics across feeding, growth, and NAM."""
        patient = await cls.get_patient_for_user(db, current_user, patient_id)

        today_utc = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today_utc, time.min, tzinfo=timezone.utc)

        # Feeding aggregates
        feeding_agg_res = await db.execute(
            select(
                func.coalesce(func.sum(FeedingLog.volume_ml), Decimal("0.0")),
                func.count(FeedingLog.id),
            ).where(
                FeedingLog.patient_id == patient.id,
                FeedingLog.logged_at >= today_start,
            )
        )
        today_volume, today_feeds = feeding_agg_res.one()

        # Last feeding log
        last_feeding_res = await db.execute(
            select(FeedingLog)
            .where(FeedingLog.patient_id == patient.id)
            .order_by(FeedingLog.logged_at.desc())
            .limit(1)
        )
        last_feeding = last_feeding_res.scalar_one_or_none()

        # Last 2 growth records
        growth_res = await db.execute(
            select(GrowthRecord)
            .where(GrowthRecord.patient_id == patient.id)
            .order_by(GrowthRecord.recorded_at.desc(), GrowthRecord.created_at.desc())
            .limit(2)
        )
        growth_rows = growth_res.scalars().all()
        latest_growth = growth_rows[0] if len(growth_rows) > 0 else None
        previous_growth = growth_rows[1] if len(growth_rows) > 1 else None

        # NAM aggregates
        today_nam_res = await db.execute(
            select(func.coalesce(func.sum(NAMTapingLog.hours_worn), 0)).where(
                NAMTapingLog.patient_id == patient.id,
                NAMTapingLog.logged_at >= today_start,
            )
        )
        today_nam_hours = today_nam_res.scalar() or 0

        latest_nam_res = await db.execute(
            select(NAMTapingLog)
            .where(NAMTapingLog.patient_id == patient.id)
            .order_by(NAMTapingLog.logged_at.desc())
            .limit(1)
        )
        latest_nam = latest_nam_res.scalar_one_or_none()

        guidance_notes = [
            "General tip: Semi-upright positioning (45° to 60°) is commonly recommended during infant feeding.",
            "General tip: Frequent burping breaks can help reduce swallowed air during feeding.",
            "Record daily observations to share with your multidisciplinary cleft care team.",
            "Inspect cheek and lip skin daily during tape routines and report any irritation to your team.",
        ]

        return CareOverviewResponse(
            patient_id=patient.id,
            today_feeding_volume_ml=Decimal(str(today_volume)),
            today_feeding_count=today_feeds,
            last_feeding=FeedingLogResponse.model_validate(last_feeding) if last_feeding else None,
            latest_growth=GrowthRecordResponse.model_validate(latest_growth) if latest_growth else None,
            previous_growth=GrowthRecordResponse.model_validate(previous_growth) if previous_growth else None,
            latest_nam_log=NAMTapingLogResponse.model_validate(latest_nam) if latest_nam else None,
            today_nam_hours=min(today_nam_hours, 24),
            guidance_notes=guidance_notes,
        )
