from datetime import date, datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.models.journey import MilestoneStatus


class MilestoneNoteCreateRequest(BaseModel):
    note_text: str = Field(..., min_length=1, max_length=2000, description="Personal memory or clinical note text")
    photo_s3_key: Optional[str] = Field(default=None, max_length=500, description="Optional S3 photo key")

    model_config = ConfigDict(extra="forbid")


class MilestoneNoteResponse(BaseModel):
    id: uuid.UUID
    milestone_id: uuid.UUID
    user_id: uuid.UUID
    note_text: str
    photo_s3_key: Optional[str] = None
    created_at: datetime
    author_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MilestoneUpdateRequest(BaseModel):
    status: Optional[MilestoneStatus] = Field(default=None, description="New milestone status")
    target_date: Optional[date] = Field(default=None, description="Updated target date")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")

    model_config = ConfigDict(extra="forbid")


class JourneyMilestoneResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    stage_id: int
    title: str
    description: str
    target_age_months: Optional[int] = None
    status: MilestoneStatus
    is_custom: bool = False
    target_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    notes_count: int = 0
    notes: List[MilestoneNoteResponse] = []

    model_config = ConfigDict(from_attributes=True)


class JourneyStageResponse(BaseModel):
    id: int
    stage_number: int
    title: str
    age_range_label: str
    description: str
    color_hex: str
    status: str = "upcoming"  # completed, in_progress, upcoming
    milestones: List[JourneyMilestoneResponse] = []
    total_milestones: int = 0
    completed_milestones: int = 0
    progress_percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class JourneyPatientSummary(BaseModel):
    id: uuid.UUID
    display_name: str
    date_of_birth: date
    gender: str
    cleft_lip: str
    cleft_palate: str
    cleft_alveolus: str

    model_config = ConfigDict(from_attributes=True)


class JourneySummaryResponse(BaseModel):
    total_milestones: int = 0
    completed_milestones: int = 0
    in_progress_milestones: int = 0
    upcoming_milestones: int = 0
    overall_progress_percentage: float = 0.0
    current_stage_number: Optional[int] = None
    current_stage_title: Optional[str] = None


class JourneyOverviewResponse(BaseModel):
    patient: Optional[JourneyPatientSummary] = None
    stages: List[JourneyStageResponse] = []
    summary: JourneySummaryResponse = Field(default_factory=JourneySummaryResponse)
