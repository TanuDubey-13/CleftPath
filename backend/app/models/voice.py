from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.journey import JourneyStage


class VoiceExercise(Base, UUIDMixin):
    __tablename__ = "voice_exercises"

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    target_phonemes: Mapped[List[str]] = mapped_column(ARRAY(String(50)), nullable=False)
    stage_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("journey_stages.id"), nullable=True)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String(30), default="beginner", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    stage: Mapped[Optional["JourneyStage"]] = relationship("JourneyStage", back_populates="voice_exercises")
    sessions: Mapped[List["VoiceSession"]] = relationship("VoiceSession", back_populates="exercise")


class VoiceSession(Base, UUIDMixin):
    __tablename__ = "voice_sessions"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exercise_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("voice_exercises.id", ondelete="SET NULL"), nullable=True
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    audio_s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    repetition_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    dsp_features_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    parent_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="voice_sessions")
    exercise: Mapped[Optional["VoiceExercise"]] = relationship("VoiceExercise", back_populates="sessions")
