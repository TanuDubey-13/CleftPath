from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Citation & Grounding Schemas
# ============================================================================

class PathGuideCitation(BaseModel):
    article_id: Optional[uuid.UUID] = None
    title: str
    category: str
    slug: Optional[str] = None
    summary: Optional[str] = None


# ============================================================================
# Message Schemas
# ============================================================================

class PathGuideMessageResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    role: str
    content: str
    citations: List[PathGuideCitation] = Field(default_factory=list)
    safety_flags: Dict[str, Any] = Field(default_factory=dict)
    tokens_used: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PathGuideMessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000, description="User prompt text")


class PaginatedPathGuideMessagesResponse(BaseModel):
    items: List[PathGuideMessageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============================================================================
# Thread Schemas
# ============================================================================

class PathGuideThreadResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: Optional[PathGuideMessageResponse] = None

    model_config = ConfigDict(from_attributes=True)


class PathGuideThreadCreateRequest(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    title: Optional[str] = Field(default="Care Conversation", max_length=200)
    initial_message: Optional[str] = Field(default=None, max_length=4000)


class PathGuideThreadUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class PaginatedPathGuideThreadsResponse(BaseModel):
    items: List[PathGuideThreadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============================================================================
# Suggested Prompts Schema
# ============================================================================

class PathGuideSuggestedPrompt(BaseModel):
    id: str
    category: str
    prompt: str
    description: str


class PathGuideSuggestedPromptsResponse(BaseModel):
    prompts: List[PathGuideSuggestedPrompt]
