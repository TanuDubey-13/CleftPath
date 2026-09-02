from datetime import date, datetime, timezone
from decimal import Decimal
import enum
from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class FeedingBottleType(str, enum.Enum):
    DR_BROWNS_SPECIALTY = "dr_browns_specialty"
    PIGEON_CLEFT = "pigeon_cleft"
    MEDELA_SPECIALNEEDS_HABERMAN = "medela_specialneeds_haberman"
    SYRINGE_WITH_TUBING = "syringe_with_tubing"
    SUPPLEMENTAL_NURSING = "supplemental_nursing"
    CUP_OPEN = "cup_open"
    STANDARD_BOTTLE = "standard_bottle"
    OTHER = "other"


class FeedingLog(Base, UUIDMixin):
    __tablename__ = "feeding_logs"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    bottle_type: Mapped[FeedingBottleType] = mapped_column(
        Enum(FeedingBottleType, name="feeding_bottle_type", native_enum=True),
        nullable=False,
    )
    volume_ml: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    burping_breaks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reflux_severity: Mapped[str] = mapped_column(String(50), default="none", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="feeding_logs")


class GrowthRecord(Base, UUIDMixin):
    __tablename__ = "growth_records"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recorded_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 3), nullable=False)
    height_cm: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    head_circumference_cm: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    weight_percentile: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    height_percentile: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="growth_records")


class NAMTapingLog(Base, UUIDMixin):
    __tablename__ = "nam_taping_logs"
    __table_args__ = (
        CheckConstraint("hours_worn >= 0 AND hours_worn <= 24", name="check_nam_hours_worn_range"),
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    hours_worn: Mapped[int] = mapped_column(Integer, nullable=False)
    appliance_cleaned: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tape_changed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    skin_condition: Mapped[str] = mapped_column(String(100), default="normal", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="nam_taping_logs")


class CareTeamMember(Base, UUIDMixin):
    __tablename__ = "care_team_members"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    specialist_name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    clinic_or_hospital: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="care_team_members")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="care_team_member")


class Appointment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "appointments"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    care_team_member_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("care_team_members.id", ondelete="SET NULL"), nullable=True
    )
    specialist_name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    clinic_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    prep_questions: Mapped[dict] = mapped_column(JSONB, default=list, nullable=False)
    summary_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="scheduled", nullable=False)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    care_team_member: Mapped[Optional["CareTeamMember"]] = relationship("CareTeamMember", back_populates="appointments")
