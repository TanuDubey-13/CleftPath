from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Voice Exercise Schemas
# ============================================================================

class VoiceExerciseResponse(BaseModel):
    id: uuid.UUID
    title: str
    target_phonemes: List[str]
    stage_id: Optional[int] = None
    prompt_text: str
    instructions: str
    difficulty_level: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedVoiceExercisesResponse(BaseModel):
    items: List[VoiceExerciseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============================================================================
# Voice Session Schemas
# ============================================================================

class VoiceSessionResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    exercise_id: Optional[uuid.UUID] = None
    recorded_at: datetime
    audio_s3_key: str
    duration_seconds: int
    repetition_count: int
    dsp_features_json: Dict[str, Any] = Field(default_factory=dict)
    parent_notes: Optional[str] = None
    created_at: datetime
    exercise: Optional[VoiceExerciseResponse] = None

    model_config = ConfigDict(from_attributes=True)


class VoiceSessionCreateRequest(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    exercise_id: Optional[uuid.UUID] = Field(None, description="Linked voice exercise ID")
    recorded_at: Optional[datetime] = None
    duration_seconds: int = Field(..., ge=1, le=3600, description="Practice duration in seconds")
    repetition_count: int = Field(default=1, ge=1, le=100, description="Number of repetitions completed")
    parent_notes: Optional[str] = Field(None, max_length=1000, description="Parent or caregiver practice observations")
    audio_s3_key: Optional[str] = Field(default="local_session", max_length=500, description="Local or private storage key")
    dsp_features_json: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Acoustic features if recorded")


class VoiceSessionUpdateRequest(BaseModel):
    duration_seconds: Optional[int] = Field(None, ge=1, le=3600)
    repetition_count: Optional[int] = Field(None, ge=1, le=100)
    parent_notes: Optional[str] = Field(None, max_length=1000)


class PaginatedVoiceSessionsResponse(BaseModel):
    items: List[VoiceSessionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    total_practice_minutes: int
    total_sessions_count: int


# ============================================================================
# Voice Overview Schemas
# ============================================================================

class VoiceOverviewResponse(BaseModel):
    patient_id: uuid.UUID
    total_sessions_count: int
    total_practice_minutes: int
    unique_exercises_practiced: int
    last_session: Optional[VoiceSessionResponse] = None
    practice_guidance_notes: List[str] = Field(default_factory=list)
