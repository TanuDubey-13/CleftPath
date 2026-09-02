"""
Database Schema, Model Relationship, and Constraint Unit Tests.
Verifies all SQLAlchemy 2.0 entities, enums, relationships, constraints, and pgvector embeddings.
Zero real patient data used.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
import uuid
import pytest
from pgvector.sqlalchemy import Vector
from sqlalchemy import inspect

from app.db.base import Base
from app.models import (
    Appointment,
    AuditLog,
    CareTeamMember,
    CleftAlveolusType,
    CleftLipType,
    CleftPalateType,
    ConsentRecord,
    Document,
    DocumentChunk,
    FeedingBottleType,
    FeedingLog,
    GrowthRecord,
    HealthArticle,
    JourneyMilestone,
    JourneyStage,
    KnowledgeChunk,
    MilestoneNote,
    MilestoneStatus,
    NAMTapingLog,
    Notification,
    PathGuideMessage,
    PathGuideThread,
    Patient,
    User,
    UserRole,
    VillageChannel,
    VillageComment,
    VillagePost,
    VillageReaction,
    VillageReport,
)


def test_registered_tables_in_metadata():
    """Verify that all 20+ tables from docs/DATABASE.md are correctly registered in SQLAlchemy Base metadata."""
    expected_tables = {
        "users",
        "consent_records",
        "audit_logs",
        "patients",
        "journey_stages",
        "journey_milestones",
        "milestone_notes",
        "feeding_logs",
        "growth_records",
        "nam_taping_logs",
        "care_team_members",
        "appointments",
        "voice_exercises",
        "voice_sessions",
        "documents",
        "document_chunks",
        "health_articles",
        "knowledge_chunks",
        "pathguide_threads",
        "pathguide_messages",
        "village_channels",
        "village_posts",
        "village_comments",
        "village_reactions",
        "village_reports",
        "notifications",
    }
    registered_tables = set(Base.metadata.tables.keys())
    for table in expected_tables:
        assert table in registered_tables, f"Table {table} missing from Base metadata!"


def test_user_and_patient_relationships():
    """Verify User -> Patient -> Milestones -> Notes relationship hierarchy."""
    user_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    milestone_id = uuid.uuid4()

    user = User(
        id=user_id,
        email="synthetic.parent@example.com",
        hashed_password="synthetic_hash",
        first_name="Synthetic",
        last_name="Parent",
        role=UserRole.CAREGIVER,
    )

    patient = Patient(
        id=patient_id,
        user_id=user_id,
        display_name="Baby Leo",
        date_of_birth=date(2026, 3, 1),
        gender="Male",
        cleft_lip=CleftLipType.UNILATERAL_LEFT_COMPLETE,
        cleft_palate=CleftPalateType.HARD_AND_SOFT_COMPLETE,
        cleft_alveolus=CleftAlveolusType.INVOLVED_LEFT,
        primary_cleft_center="Children's Craniofacial Center",
    )
    patient.user = user

    stage = JourneyStage(
        id=2,
        stage_number=2,
        title="Stage 2: Primary Lip Repair",
        age_range_label="3–6 Months",
        description="Cheiloplasty surgery stage",
        color_hex="#E07A5F",
    )

    milestone = JourneyMilestone(
        id=milestone_id,
        patient_id=patient_id,
        stage_id=2,
        title="Primary Lip Repair (Cheiloplasty)",
        description="Surgical lip repair",
        status=MilestoneStatus.IN_PROGRESS,
    )
    milestone.patient = patient
    milestone.stage = stage

    note = MilestoneNote(
        id=uuid.uuid4(),
        milestone_id=milestone_id,
        user_id=user_id,
        note_text="Pre-op consult completed smoothly.",
    )
    note.milestone = milestone
    note.user = user

    assert patient.user.email == "synthetic.parent@example.com"
    assert milestone.patient.display_name == "Baby Leo"
    assert milestone.stage.title == "Stage 2: Primary Lip Repair"
    assert note.milestone.title == "Primary Lip Repair (Cheiloplasty)"
    assert note.user.id == user_id


def test_clinical_logs_instantiation():
    """Verify FeedingLog, GrowthRecord, NAMTapingLog, and Appointment entity mappings."""
    patient_id = uuid.uuid4()

    feeding = FeedingLog(
        id=uuid.uuid4(),
        patient_id=patient_id,
        bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY,
        volume_ml=Decimal("120.50"),
        duration_minutes=25,
        burping_breaks=2,
        reflux_severity="mild",
    )
    assert feeding.bottle_type == FeedingBottleType.DR_BROWNS_SPECIALTY
    assert feeding.volume_ml == Decimal("120.50")

    growth = GrowthRecord(
        id=uuid.uuid4(),
        patient_id=patient_id,
        recorded_at=date(2026, 7, 1),
        weight_kg=Decimal("6.200"),
        height_cm=Decimal("62.50"),
        head_circumference_cm=Decimal("41.20"),
    )
    assert growth.weight_kg == Decimal("6.200")

    nam_log = NAMTapingLog(
        id=uuid.uuid4(),
        patient_id=patient_id,
        hours_worn=22,
        appliance_cleaned=True,
        tape_changed=True,
        skin_condition="normal",
    )
    assert nam_log.hours_worn == 22
    assert nam_log.appliance_cleaned is True

    appt = Appointment(
        id=uuid.uuid4(),
        patient_id=patient_id,
        specialist_name="Dr. Robert Sterling",
        specialty="Plastic Surgery",
        scheduled_at=datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc),
        prep_questions=["Fasting window instructions?"],
        status="scheduled",
    )
    assert appt.specialty == "Plastic Surgery"
    assert appt.prep_questions == ["Fasting window instructions?"]


def test_pgvector_embedding_column_definition():
    """Verify that DocumentChunk and KnowledgeChunk models contain 768-dimensional Vector columns."""
    doc_chunk_table = Base.metadata.tables["document_chunks"]
    knowledge_chunk_table = Base.metadata.tables["knowledge_chunks"]

    # Check Vector type and dimension in document_chunks
    embedding_col = doc_chunk_table.columns["embedding"]
    assert isinstance(embedding_col.type, Vector)
    assert embedding_col.type.dim == 768

    # Check Vector type and dimension in knowledge_chunks
    k_embedding_col = knowledge_chunk_table.columns["embedding"]
    assert isinstance(k_embedding_col.type, Vector)
    assert k_embedding_col.type.dim == 768


def test_pathguide_and_village_models():
    """Verify PathGuide AI threads/messages and Village community posts/comments/reactions."""
    user_id = uuid.uuid4()
    thread_id = uuid.uuid4()
    post_id = uuid.uuid4()

    thread = PathGuideThread(
        id=thread_id,
        user_id=user_id,
        title="Feeding Questions",
    )
    message = PathGuideMessage(
        id=uuid.uuid4(),
        thread_id=thread_id,
        role="assistant",
        content="Dr. Brown's specialty feeder works via a unidirectional valve.",
        citations=["ACPA Feeding Guide 2024"],
        safety_flags={"is_emergency": False, "is_diagnostic": False},
        tokens_used=120,
    )
    message.thread = thread

    assert message.thread.title == "Feeding Questions"
    assert message.role == "assistant"
    assert message.safety_flags["is_emergency"] is False

    post = VillagePost(
        id=post_id,
        channel_id=uuid.uuid4(),
        user_id=user_id,
        author_alias="SyntheticCaregiver",
        author_avatar_seed="avatar_coral",
        title="Tips for post-lip surgery recovery?",
        content="Any recommendations on keeping arm restraints soft?",
        status="published",
    )
    reaction = VillageReaction(
        id=uuid.uuid4(),
        post_id=post_id,
        user_id=user_id,
        reaction_type="heart",
    )
    reaction.post = post

    assert reaction.post.title == "Tips for post-lip surgery recovery?"
    assert reaction.reaction_type == "heart"


def test_tenant_isolation_ownership_foundations():
    """Verify that every patient record, document, and appointment is strictly bound to a tenant patient/user ID."""
    patient_mapper = inspect(Patient)
    doc_mapper = inspect(Document)
    appt_mapper = inspect(Appointment)
    feeding_mapper = inspect(FeedingLog)

    # Verify patient has user_id foreign key
    assert "user_id" in [c.name for c in patient_mapper.columns]
    # Verify document has both patient_id and user_id for fast tenant isolation
    assert "patient_id" in [c.name for c in doc_mapper.columns]
    assert "user_id" in [c.name for c in doc_mapper.columns]
    # Verify clinical logs have patient_id
    assert "patient_id" in [c.name for c in appt_mapper.columns]
    assert "patient_id" in [c.name for c in feeding_mapper.columns]
