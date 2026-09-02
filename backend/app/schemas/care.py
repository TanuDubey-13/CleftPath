from datetime import date, datetime
from decimal import Decimal
import enum
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.models.clinical import FeedingBottleType


class RefluxSeverity(str, enum.Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


# ============================================================================
# Feeding Schemas
# ============================================================================

class FeedingLogResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    logged_at: datetime
    bottle_type: FeedingBottleType
    volume_ml: Decimal
    duration_minutes: int
    burping_breaks: int
    reflux_severity: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedingLogCreateRequest(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    logged_at: Optional[datetime] = None
    bottle_type: FeedingBottleType = Field(..., description="Specialty feeding method or bottle type")
    volume_ml: Decimal = Field(..., ge=0, le=1000, description="Volume fed in milliliters")
    duration_minutes: int = Field(..., ge=1, le=180, description="Feeding session duration in minutes")
    burping_breaks: int = Field(default=0, ge=0, le=50, description="Number of burping intervals")
    reflux_severity: RefluxSeverity = Field(default=RefluxSeverity.NONE, description="Reflux severity level")
    notes: Optional[str] = Field(None, max_length=1000, description="Feeding notes or observations")


class FeedingLogUpdateRequest(BaseModel):
    logged_at: Optional[datetime] = None
    bottle_type: Optional[FeedingBottleType] = None
    volume_ml: Optional[Decimal] = Field(None, ge=0, le=1000)
    duration_minutes: Optional[int] = Field(None, ge=1, le=180)
    burping_breaks: Optional[int] = Field(None, ge=0, le=50)
    reflux_severity: Optional[RefluxSeverity] = None
    notes: Optional[str] = Field(None, max_length=1000)


class PaginatedFeedingLogsResponse(BaseModel):
    items: List[FeedingLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    today_total_volume_ml: Decimal
    today_total_feeds: int


# ============================================================================
# Growth Schemas
# ============================================================================

class GrowthRecordResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    recorded_at: date
    weight_kg: Decimal
    height_cm: Optional[Decimal] = None
    head_circumference_cm: Optional[Decimal] = None
    weight_percentile: Optional[Decimal] = None
    height_percentile: Optional[Decimal] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GrowthRecordCreateRequest(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    recorded_at: date = Field(..., description="Date of physical measurement")
    weight_kg: Decimal = Field(..., ge=0.5, le=50.0, description="Weight in kilograms")
    height_cm: Optional[Decimal] = Field(None, ge=20.0, le=150.0, description="Length / height in centimeters")
    head_circumference_cm: Optional[Decimal] = Field(None, ge=15.0, le=70.0, description="Head circumference in centimeters")
    weight_percentile: Optional[Decimal] = Field(None, ge=0, le=100, description="WHO reference percentile if calculated")
    height_percentile: Optional[Decimal] = Field(None, ge=0, le=100, description="WHO reference percentile if calculated")


class GrowthRecordUpdateRequest(BaseModel):
    recorded_at: Optional[date] = None
    weight_kg: Optional[Decimal] = Field(None, ge=0.5, le=50.0)
    height_cm: Optional[Decimal] = Field(None, ge=20.0, le=150.0)
    head_circumference_cm: Optional[Decimal] = Field(None, ge=15.0, le=70.0)
    weight_percentile: Optional[Decimal] = Field(None, ge=0, le=100)
    height_percentile: Optional[Decimal] = Field(None, ge=0, le=100)


class PaginatedGrowthRecordsResponse(BaseModel):
    items: List[GrowthRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    latest_weight_kg: Optional[Decimal] = None


# ============================================================================
# NAM / Taping Schemas
# ============================================================================

class NAMTapingLogResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    logged_at: datetime
    hours_worn: int
    appliance_cleaned: bool
    tape_changed: bool
    skin_condition: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NAMTapingLogCreateRequest(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    logged_at: Optional[datetime] = None
    hours_worn: int = Field(..., ge=0, le=24, description="Hours appliance was worn in 24-hour cycle")
    appliance_cleaned: bool = Field(default=True, description="Appliance was cleaned with mild soap/water")
    tape_changed: bool = Field(default=False, description="Facial tape and elastics were replaced")
    skin_condition: str = Field(default="normal", max_length=100, description="Cheek/lip skin condition (normal, mild_redness, irritation)")
    notes: Optional[str] = Field(None, max_length=1000, description="Observations on appliance fit or retention")


class NAMTapingLogUpdateRequest(BaseModel):
    logged_at: Optional[datetime] = None
    hours_worn: Optional[int] = Field(None, ge=0, le=24)
    appliance_cleaned: Optional[bool] = None
    tape_changed: Optional[bool] = None
    skin_condition: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


class PaginatedNAMLogsResponse(BaseModel):
    items: List[NAMTapingLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    today_hours_worn: int


# ============================================================================
# Care Overview Schema
# ============================================================================

class CareOverviewResponse(BaseModel):
    patient_id: uuid.UUID
    today_feeding_volume_ml: Decimal
    today_feeding_count: int
    last_feeding: Optional[FeedingLogResponse] = None
    latest_growth: Optional[GrowthRecordResponse] = None
    previous_growth: Optional[GrowthRecordResponse] = None
    latest_nam_log: Optional[NAMTapingLogResponse] = None
    today_nam_hours: int = 0
    guidance_notes: List[str] = Field(default_factory=list)
