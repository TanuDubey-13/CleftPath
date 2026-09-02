from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# Channel Schemas
# ============================================================================

class VillageChannelResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str
    stage_id: Optional[int] = None
    is_private: bool = False
    posts_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class PaginatedVillageChannelsResponse(BaseModel):
    items: List[VillageChannelResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============================================================================
# Post Schemas
# ============================================================================

class VillagePostCreateRequest(BaseModel):
    channel_id: uuid.UUID
    title: str = Field(..., min_length=3, max_length=255, description="Post title")
    content: str = Field(..., min_length=5, max_length=10000, description="Post content text")
    author_alias: Optional[str] = Field(default=None, max_length=100, description="Display alias (defaults to user name)")
    author_avatar_seed: Optional[str] = Field(default="avatar1", max_length=100)

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty.")
        return v.strip()

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content cannot be empty.")
        return v.strip()


class VillagePostUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    content: Optional[str] = Field(default=None, min_length=5, max_length=10000)


class VillagePostResponse(BaseModel):
    id: uuid.UUID
    channel_id: uuid.UUID
    channel_name: Optional[str] = None
    channel_slug: Optional[str] = None
    user_id: uuid.UUID
    author_alias: str
    author_avatar_seed: str
    title: str
    content: str
    status: str
    is_flagged: bool
    upvotes_count: int
    comments_count: int
    has_reacted: bool = False
    user_reaction: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedVillagePostsResponse(BaseModel):
    items: List[VillagePostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============================================================================
# Comment Schemas
# ============================================================================

class VillageCommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=3000, description="Comment text")
    author_alias: Optional[str] = Field(default=None, max_length=100)


class VillageCommentUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=3000, description="Updated comment text")


class VillageCommentResponse(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    user_id: uuid.UUID
    author_alias: str
    content: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedVillageCommentsResponse(BaseModel):
    items: List[VillageCommentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============================================================================
# Reaction Schemas
# ============================================================================

VALID_REACTION_TYPES = {"heart", "hug", "celebrate", "strength", "helpful"}

class VillageReactionRequest(BaseModel):
    reaction_type: str = Field(default="heart", description="Type of reaction: heart, hug, celebrate, strength, helpful")


class VillageReactionResponse(BaseModel):
    post_id: uuid.UUID
    reaction_type: str
    action: str  # "added" or "removed"
    upvotes_count: int
    has_reacted: bool


# ============================================================================
# Report & Moderation Schemas
# ============================================================================

VALID_REPORT_REASONS = {
    "harassment",
    "medical_misinformation",
    "hate_or_abuse",
    "spam",
    "inappropriate_content",
    "privacy_violation",
    "other",
}

class VillageReportCreateRequest(BaseModel):
    reason: str = Field(..., description="Reporting reason category")
    details: Optional[str] = Field(default=None, max_length=2000, description="Optional description of the issue")


class VillageReportResponse(BaseModel):
    id: uuid.UUID
    post_id: Optional[uuid.UUID] = None
    comment_id: Optional[uuid.UUID] = None
    reason: str
    details: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VillageModerationActionRequest(BaseModel):
    action: str = Field(..., description="Action to take: 'dismiss', 'hide_content', 'resolve'")
    note: Optional[str] = Field(default=None, max_length=1000)


class PaginatedVillageReportsResponse(BaseModel):
    items: List[VillageReportResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
