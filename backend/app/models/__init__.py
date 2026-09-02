"""
CleftPath SQLAlchemy 2.0 Database Models
Exports all entities and enums for Alembic discovery and application use.
"""

from app.db.base import Base, TimestampMixin, UUIDMixin

# Enums
from app.models.user import UserRole
from app.models.patient import CleftLipType, CleftPalateType, CleftAlveolusType
from app.models.journey import MilestoneStatus
from app.models.clinical import FeedingBottleType

# Models
from app.models.user import User, ConsentRecord, AuditLog
from app.models.patient import Patient
from app.models.journey import JourneyStage, JourneyMilestone, MilestoneNote
from app.models.clinical import (
    FeedingLog,
    GrowthRecord,
    NAMTapingLog,
    CareTeamMember,
    Appointment,
)
from app.models.voice import VoiceExercise, VoiceSession
from app.models.document import Document, DocumentChunk
from app.models.knowledge import HealthArticle, KnowledgeChunk
from app.models.pathguide import PathGuideThread, PathGuideMessage
from app.models.village import (
    VillageChannel,
    VillagePost,
    VillageComment,
    VillageReaction,
    VillageReport,
)
from app.models.notification import Notification

__all__ = [
    # Base & Mixins
    "Base",
    "UUIDMixin",
    "TimestampMixin",
    # Enums
    "UserRole",
    "CleftLipType",
    "CleftPalateType",
    "CleftAlveolusType",
    "MilestoneStatus",
    "FeedingBottleType",
    # Models
    "User",
    "ConsentRecord",
    "AuditLog",
    "Patient",
    "JourneyStage",
    "JourneyMilestone",
    "MilestoneNote",
    "FeedingLog",
    "GrowthRecord",
    "NAMTapingLog",
    "CareTeamMember",
    "Appointment",
    "VoiceExercise",
    "VoiceSession",
    "Document",
    "DocumentChunk",
    "HealthArticle",
    "KnowledgeChunk",
    "PathGuideThread",
    "PathGuideMessage",
    "VillageChannel",
    "VillagePost",
    "VillageComment",
    "VillageReaction",
    "VillageReport",
    "Notification",
]
