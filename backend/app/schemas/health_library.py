from datetime import datetime
import math
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class HealthArticleCardResponse(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    category: str
    stage_id: Optional[int] = None
    stage_title: Optional[str] = None
    summary: str
    author_source: str
    clinical_verified_by: Optional[str] = None
    reading_time_minutes: int = Field(default=3, description="Estimated reading time in minutes")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthArticleDetailResponse(HealthArticleCardResponse):
    content_markdown: str


class HealthCategoryResponse(BaseModel):
    name: str
    article_count: int


class PaginatedHealthArticlesResponse(BaseModel):
    items: List[HealthArticleCardResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def calculate_reading_time(text: str) -> int:
    """Calculate reading time in minutes based on average 200 words per minute."""
    if not text:
        return 1
    word_count = len(text.split())
    return max(1, math.ceil(word_count / 200))
