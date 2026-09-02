import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.pathguide import PathGuideThread
    from app.models.village import VillagePost, VillageComment, VillageReport, VillageReaction
    from app.models.notification import Notification
    from app.models.document import Document
    from app.models.journey import MilestoneNote


class UserRole(str, enum.Enum):
    CAREGIVER = "caregiver"
    PATIENT_ADULT = "patient_adult"
    CLINICIAN = "clinician"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=True),
        default=UserRole.CAREGIVER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    consents: Mapped[List["ConsentRecord"]] = relationship(
        "ConsentRecord", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )
    patients: Mapped[List["Patient"]] = relationship(
        "Patient", back_populates="user", cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )
    milestone_notes: Mapped[List["MilestoneNote"]] = relationship(
        "MilestoneNote", back_populates="user", cascade="all, delete-orphan"
    )
    pathguide_threads: Mapped[List["PathGuideThread"]] = relationship(
        "PathGuideThread", back_populates="user", cascade="all, delete-orphan"
    )
    village_posts: Mapped[List["VillagePost"]] = relationship(
        "VillagePost", back_populates="user", cascade="all, delete-orphan"
    )
    village_comments: Mapped[List["VillageComment"]] = relationship(
        "VillageComment", back_populates="user", cascade="all, delete-orphan"
    )
    village_reports: Mapped[List["VillageReport"]] = relationship(
        "VillageReport", back_populates="reported_by", cascade="all, delete-orphan"
    )
    village_reactions: Mapped[List["VillageReaction"]] = relationship(
        "VillageReaction", back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )


class ConsentRecord(Base, UUIDMixin):
    __tablename__ = "consent_records"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    terms_version: Mapped[str] = mapped_column(String(50), nullable=False)
    privacy_version: Mapped[str] = mapped_column(String(50), nullable=False)
    ai_safety_disclaimer_accepted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_retention_accepted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    consented_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="consents")


class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
