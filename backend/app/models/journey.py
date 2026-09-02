from datetime import date, datetime
import enum
from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.user import User
    from app.models.voice import VoiceExercise
    from app.models.knowledge import HealthArticle
    from app.models.village import VillageChannel


class MilestoneStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class JourneyStage(Base):
    __tablename__ = "journey_stages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stage_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    age_range_label: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    color_hex: Mapped[str] = mapped_column(String(10), default="#0F4C5C", nullable=False)

    # Relationships
    milestones: Mapped[List["JourneyMilestone"]] = relationship("JourneyMilestone", back_populates="stage")
    voice_exercises: Mapped[List["VoiceExercise"]] = relationship("VoiceExercise", back_populates="stage")
    articles: Mapped[List["HealthArticle"]] = relationship("HealthArticle", back_populates="stage")
    channels: Mapped[List["VillageChannel"]] = relationship("VillageChannel", back_populates="stage")


class JourneyMilestone(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "journey_milestones"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("journey_stages.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_age_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[MilestoneStatus] = mapped_column(
        Enum(MilestoneStatus, name="milestone_status", native_enum=True, values_callable=lambda obj: [e.value for e in obj]),
        default=MilestoneStatus.UPCOMING,
        nullable=False,
    )
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="milestones")
    stage: Mapped["JourneyStage"] = relationship("JourneyStage", back_populates="milestones")
    notes: Mapped[List["MilestoneNote"]] = relationship(
        "MilestoneNote", back_populates="milestone", cascade="all, delete-orphan"
    )


class MilestoneNote(Base, UUIDMixin):
    __tablename__ = "milestone_notes"

    milestone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("journey_milestones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    photo_s3_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    milestone: Mapped["JourneyMilestone"] = relationship("JourneyMilestone", back_populates="notes")
    user: Mapped["User"] = relationship("User", back_populates="milestone_notes")
