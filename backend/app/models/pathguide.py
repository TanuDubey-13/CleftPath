from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.patient import Patient


class PathGuideThread(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pathguide_threads"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    patient_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), default="Care Conversation", nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="pathguide_threads")
    patient: Mapped[Optional["Patient"]] = relationship("Patient", back_populates="pathguide_threads")
    messages: Mapped[List["PathGuideMessage"]] = relationship(
        "PathGuideMessage", back_populates="thread", cascade="all, delete-orphan"
    )


class PathGuideMessage(Base, UUIDMixin):
    __tablename__ = "pathguide_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_pathguide_message_role"),
    )

    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pathguide_threads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    safety_flags: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    thread: Mapped["PathGuideThread"] = relationship("PathGuideThread", back_populates="messages")
