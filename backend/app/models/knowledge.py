from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import uuid
from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.journey import JourneyStage


class HealthArticle(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "health_articles"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stage_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("journey_stages.id"), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    author_source: Mapped[str] = mapped_column(String(255), nullable=False)
    clinical_verified_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)

    # Relationships
    stage: Mapped[Optional["JourneyStage"]] = relationship("JourneyStage", back_populates="articles")
    chunks: Mapped[List["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk", back_populates="article", cascade="all, delete-orphan"
    )


class KnowledgeChunk(Base, UUIDMixin):
    __tablename__ = "knowledge_chunks"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("health_articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768), nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    article: Mapped["HealthArticle"] = relationship("HealthArticle", back_populates="chunks")
