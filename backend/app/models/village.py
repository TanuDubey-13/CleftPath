from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.journey import JourneyStage


class VillageChannel(Base, UUIDMixin):
    __tablename__ = "village_channels"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    stage_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("journey_stages.id"), nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    stage: Mapped[Optional["JourneyStage"]] = relationship("JourneyStage", back_populates="channels")
    posts: Mapped[List["VillagePost"]] = relationship(
        "VillagePost", back_populates="channel", cascade="all, delete-orphan"
    )


class VillagePost(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "village_posts"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("village_channels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_alias: Mapped[str] = mapped_column(String(100), nullable=False)
    author_avatar_seed: Mapped[str] = mapped_column(String(100), default="avatar1", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="published", nullable=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    upvotes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    channel: Mapped["VillageChannel"] = relationship("VillageChannel", back_populates="posts")
    user: Mapped["User"] = relationship("User", back_populates="village_posts")
    comments: Mapped[List["VillageComment"]] = relationship(
        "VillageComment", back_populates="post", cascade="all, delete-orphan"
    )
    reports: Mapped[List["VillageReport"]] = relationship(
        "VillageReport", back_populates="post", cascade="all, delete-orphan"
    )
    reactions: Mapped[List["VillageReaction"]] = relationship(
        "VillageReaction", back_populates="post", cascade="all, delete-orphan"
    )


class VillageComment(Base, UUIDMixin):
    __tablename__ = "village_comments"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("village_posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_alias: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="published", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    post: Mapped["VillagePost"] = relationship("VillagePost", back_populates="comments")
    user: Mapped["User"] = relationship("User", back_populates="village_comments")
    reports: Mapped[List["VillageReport"]] = relationship(
        "VillageReport", back_populates="comment", cascade="all, delete-orphan"
    )


class VillageReaction(Base, UUIDMixin):
    __tablename__ = "village_reactions"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", "reaction_type", name="uq_village_reaction"),
    )

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("village_posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reaction_type: Mapped[str] = mapped_column(String(50), default="heart", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    post: Mapped["VillagePost"] = relationship("VillagePost", back_populates="reactions")
    user: Mapped["User"] = relationship("User", back_populates="village_reactions")


class VillageReport(Base, UUIDMixin):
    __tablename__ = "village_reports"

    reported_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    post_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("village_posts.id", ondelete="CASCADE"), nullable=True, index=True
    )
    comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("village_comments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    reported_by: Mapped["User"] = relationship("User", back_populates="village_reports")
    post: Mapped[Optional["VillagePost"]] = relationship("VillagePost", back_populates="reports")
    comment: Mapped[Optional["VillageComment"]] = relationship("VillageComment", back_populates="reports")
