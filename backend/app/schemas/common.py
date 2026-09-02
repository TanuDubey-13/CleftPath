from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    page: Optional[int] = None
    limit: Optional[int] = None
    total: Optional[int] = None


class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: Optional[ResponseMeta] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = []
