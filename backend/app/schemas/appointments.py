from datetime import datetime
import enum
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class CareTeamMemberSummary(BaseModel):
    id: uuid.UUID
    specialist_name: str
    specialty: str
    clinic_or_hospital: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    care_team_member_id: Optional[uuid.UUID] = None
    specialist_name: str
    specialty: str
    clinic_location: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = 30
    prep_questions: List[str] = Field(default_factory=list)
    summary_notes: Optional[str] = None
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    care_team_member: Optional[CareTeamMemberSummary] = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentCreateRequest(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    specialist_name: str = Field(..., min_length=1, max_length=150, description="Name of the healthcare specialist")
    specialty: str = Field(..., min_length=1, max_length=100, description="Clinical specialty (e.g. Plastic Surgeon, SLP)")
    clinic_location: Optional[str] = Field(None, max_length=255, description="Clinic room or hospital address")
    scheduled_at: datetime = Field(..., description="Timezone-aware scheduled date and time")
    duration_minutes: int = Field(default=30, ge=10, le=480, description="Visit duration in minutes")
    prep_questions: Optional[List[str]] = Field(default_factory=list, description="Questions to ask the specialist")
    summary_notes: Optional[str] = Field(None, max_length=2000, description="Post-visit instructions or private caregiver notes")
    care_team_member_id: Optional[uuid.UUID] = None


class AppointmentUpdateRequest(BaseModel):
    specialist_name: Optional[str] = Field(None, min_length=1, max_length=150)
    specialty: Optional[str] = Field(None, min_length=1, max_length=100)
    clinic_location: Optional[str] = Field(None, max_length=255)
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=10, le=480)
    prep_questions: Optional[List[str]] = None
    summary_notes: Optional[str] = Field(None, max_length=2000)
    status: Optional[AppointmentStatus] = None
    care_team_member_id: Optional[uuid.UUID] = None


class PaginatedAppointmentsResponse(BaseModel):
    items: List[AppointmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    upcoming_count: int
    past_count: int
    next_appointment: Optional[AppointmentResponse] = None
