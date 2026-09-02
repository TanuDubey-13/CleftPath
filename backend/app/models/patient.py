from datetime import date
import enum
from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.journey import JourneyMilestone
    from app.models.clinical import (
        Appointment,
        CareTeamMember,
        FeedingLog,
        GrowthRecord,
        NAMTapingLog,
    )
    from app.models.voice import VoiceSession
    from app.models.document import Document
    from app.models.pathguide import PathGuideThread


class CleftLipType(str, enum.Enum):
    NONE = "none"
    UNILATERAL_LEFT_INCOMPLETE = "unilateral_left_incomplete"
    UNILATERAL_LEFT_COMPLETE = "unilateral_left_complete"
    UNILATERAL_RIGHT_INCOMPLETE = "unilateral_right_incomplete"
    UNILATERAL_RIGHT_COMPLETE = "unilateral_right_complete"
    BILATERAL_INCOMPLETE = "bilateral_incomplete"
    BILATERAL_COMPLETE = "bilateral_complete"
    MICROFORM = "microform"


class CleftPalateType(str, enum.Enum):
    NONE = "none"
    SOFT_PALATE_ONLY = "soft_palate_only"
    HARD_AND_SOFT_INCOMPLETE = "hard_and_soft_incomplete"
    HARD_AND_SOFT_COMPLETE = "hard_and_soft_complete"
    SUBMUCOUS = "submucous"
    BIFID_UVULA = "bifid_uvula"


class CleftAlveolusType(str, enum.Enum):
    NONE = "none"
    INVOLVED_LEFT = "involved_left"
    INVOLVED_RIGHT = "involved_right"
    INVOLVED_BILATERAL = "involved_bilateral"


class Patient(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "patients"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    cleft_lip: Mapped[CleftLipType] = mapped_column(
        Enum(CleftLipType, name="cleft_lip_type", native_enum=True, values_callable=lambda obj: [e.value for e in obj]),
        default=CleftLipType.NONE,
        nullable=False,
    )
    cleft_palate: Mapped[CleftPalateType] = mapped_column(
        Enum(CleftPalateType, name="cleft_palate_type", native_enum=True, values_callable=lambda obj: [e.value for e in obj]),
        default=CleftPalateType.NONE,
        nullable=False,
    )
    cleft_alveolus: Mapped[CleftAlveolusType] = mapped_column(
        Enum(CleftAlveolusType, name="cleft_alveolus_type", native_enum=True, values_callable=lambda obj: [e.value for e in obj]),
        default=CleftAlveolusType.NONE,
        nullable=False,
    )
    primary_cleft_center: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="patients")
    milestones: Mapped[List["JourneyMilestone"]] = relationship(
        "JourneyMilestone", back_populates="patient", cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="patient", cascade="all, delete-orphan"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="patient", cascade="all, delete-orphan"
    )
    care_team_members: Mapped[List["CareTeamMember"]] = relationship(
        "CareTeamMember", back_populates="patient", cascade="all, delete-orphan"
    )
    feeding_logs: Mapped[List["FeedingLog"]] = relationship(
        "FeedingLog", back_populates="patient", cascade="all, delete-orphan"
    )
    growth_records: Mapped[List["GrowthRecord"]] = relationship(
        "GrowthRecord", back_populates="patient", cascade="all, delete-orphan"
    )
    nam_taping_logs: Mapped[List["NAMTapingLog"]] = relationship(
        "NAMTapingLog", back_populates="patient", cascade="all, delete-orphan"
    )
    voice_sessions: Mapped[List["VoiceSession"]] = relationship(
        "VoiceSession", back_populates="patient", cascade="all, delete-orphan"
    )
    pathguide_threads: Mapped[List["PathGuideThread"]] = relationship(
        "PathGuideThread", back_populates="patient"
    )
