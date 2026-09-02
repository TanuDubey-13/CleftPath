"""Create full CleftPath schema: identity, clinical, journey, documents, knowledge, voice, pathguide, village, and notifications

Revision ID: 0002_cleftpath_schema
Revises: 0001_initial_pgvector
Create Date: 2026-09-02 13:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "0002_cleftpath_schema"
down_revision: Union[str, None] = "0001_initial_pgvector"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums
    user_role_enum = postgresql.ENUM(
        "caregiver", "patient_adult", "clinician", "moderator", "admin", name="user_role", create_type=False
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)

    cleft_lip_enum = postgresql.ENUM(
        "none",
        "unilateral_left_incomplete",
        "unilateral_left_complete",
        "unilateral_right_incomplete",
        "unilateral_right_complete",
        "bilateral_incomplete",
        "bilateral_complete",
        "microform",
        name="cleft_lip_type",
        create_type=False,
    )
    cleft_lip_enum.create(op.get_bind(), checkfirst=True)

    cleft_palate_enum = postgresql.ENUM(
        "none",
        "soft_palate_only",
        "hard_and_soft_incomplete",
        "hard_and_soft_complete",
        "submucous",
        "bifid_uvula",
        name="cleft_palate_type",
        create_type=False,
    )
    cleft_palate_enum.create(op.get_bind(), checkfirst=True)

    cleft_alveolus_enum = postgresql.ENUM(
        "none",
        "involved_left",
        "involved_right",
        "involved_bilateral",
        name="cleft_alveolus_type",
        create_type=False,
    )
    cleft_alveolus_enum.create(op.get_bind(), checkfirst=True)

    milestone_status_enum = postgresql.ENUM(
        "upcoming", "in_progress", "completed", "skipped", name="milestone_status", create_type=False
    )
    milestone_status_enum.create(op.get_bind(), checkfirst=True)

    feeding_bottle_enum = postgresql.ENUM(
        "dr_browns_specialty",
        "pigeon_cleft",
        "medela_specialneeds_haberman",
        "syringe_with_tubing",
        "supplemental_nursing",
        "cup_open",
        "standard_bottle",
        "other",
        name="feeding_bottle_type",
        create_type=False,
    )
    feeding_bottle_enum.create(op.get_bind(), checkfirst=True)

    # 2. Identity & Governance
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("role", user_role_enum, nullable=False, server_default="caregiver"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_users_email", "users", ["email"])

    op.create_table(
        "consent_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("terms_version", sa.String(50), nullable=False),
        sa.Column("privacy_version", sa.String(50), nullable=False),
        sa.Column("ai_safety_disclaimer_accepted", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("data_retention_accepted", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_consent_records_user_id", "consent_records", ["user_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("idx_audit_logs_action", "audit_logs", ["action"])

    # 3. Patient & Journey Roadmap
    op.create_table(
        "patients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("cleft_lip", cleft_lip_enum, nullable=False, server_default="none"),
        sa.Column("cleft_palate", cleft_palate_enum, nullable=False, server_default="none"),
        sa.Column("cleft_alveolus", cleft_alveolus_enum, nullable=False, server_default="none"),
        sa.Column("primary_cleft_center", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_patients_user_id", "patients", ["user_id"])

    op.create_table(
        "journey_stages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("stage_number", sa.Integer(), nullable=False, unique=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("age_range_label", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("color_hex", sa.String(10), nullable=False, server_default="#0F4C5C"),
    )

    op.create_table(
        "journey_milestones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage_id", sa.Integer(), sa.ForeignKey("journey_stages.id"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("target_age_months", sa.Integer(), nullable=True),
        sa.Column("status", milestone_status_enum, nullable=False, server_default="upcoming"),
        sa.Column("is_custom", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_milestones_patient_id", "journey_milestones", ["patient_id"])
    op.create_index("idx_milestones_stage_id", "journey_milestones", ["stage_id"])

    op.create_table(
        "milestone_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("milestone_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("journey_milestones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("note_text", sa.Text(), nullable=False),
        sa.Column("photo_s3_key", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_milestone_notes_milestone_id", "milestone_notes", ["milestone_id"])

    # 4. Clinical Tracking
    op.create_table(
        "feeding_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("bottle_type", feeding_bottle_enum, nullable=False),
        sa.Column("volume_ml", sa.Numeric(6, 2), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("burping_breaks", sa.Integer(), server_default="0", nullable=False),
        sa.Column("reflux_severity", sa.String(50), server_default="none", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_feeding_patient_id_logged", "feeding_logs", ["patient_id", sa.text("logged_at DESC")])

    op.create_table(
        "growth_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recorded_at", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 3), nullable=False),
        sa.Column("height_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("head_circumference_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("weight_percentile", sa.Numeric(5, 2), nullable=True),
        sa.Column("height_percentile", sa.Numeric(5, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_growth_patient_id_recorded", "growth_records", ["patient_id", sa.text("recorded_at DESC")])

    op.create_table(
        "nam_taping_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("hours_worn", sa.Integer(), nullable=False),
        sa.Column("appliance_cleaned", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("tape_changed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("skin_condition", sa.String(100), nullable=False, server_default="normal"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("hours_worn >= 0 AND hours_worn <= 24", name="check_nam_hours_worn_range"),
    )
    op.create_index("idx_nam_patient_id_logged", "nam_taping_logs", ["patient_id", sa.text("logged_at DESC")])

    op.create_table(
        "care_team_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("specialist_name", sa.String(150), nullable=False),
        sa.Column("specialty", sa.String(100), nullable=False),
        sa.Column("clinic_or_hospital", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(50), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_care_team_patient_id", "care_team_members", ["patient_id"])

    op.create_table(
        "appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("care_team_member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("care_team_members.id", ondelete="SET NULL"), nullable=True),
        sa.Column("specialist_name", sa.String(150), nullable=False),
        sa.Column("specialty", sa.String(100), nullable=False),
        sa.Column("clinic_location", sa.String(255), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), server_default="30", nullable=False),
        sa.Column("prep_questions", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("summary_notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), server_default="scheduled", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_appointments_patient_scheduled", "appointments", ["patient_id", "scheduled_at"])

    # 5. Voice Journey (Speech Practice)
    op.create_table(
        "voice_exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("target_phonemes", postgresql.ARRAY(sa.String(50)), nullable=False),
        sa.Column("stage_id", sa.Integer(), sa.ForeignKey("journey_stages.id"), nullable=True),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("difficulty_level", sa.String(30), server_default="beginner", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "voice_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("voice_exercises.id", ondelete="SET NULL"), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("audio_s3_key", sa.String(500), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("repetition_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("dsp_features_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("parent_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_voice_sessions_patient_id", "voice_sessions", ["patient_id"])

    # 6. Documents, Knowledge Base & pgvector
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("s3_key", sa.String(500), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("document_type", sa.String(100), server_default="general", nullable=False),
        sa.Column("ocr_status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("ocr_raw_text", sa.Text(), nullable=True),
        sa.Column("extracted_summary", sa.Text(), nullable=True),
        sa.Column("structured_metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_documents_patient_id", "documents", ["patient_id"])
    op.create_index("idx_documents_user_id", "documents", ["user_id"])

    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_document_chunks_document_id", "document_chunks", ["document_id"])
    op.execute(
        "CREATE INDEX idx_document_chunks_embedding ON document_chunks "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )

    op.create_table(
        "health_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("stage_id", sa.Integer(), sa.ForeignKey("journey_stages.id"), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column("author_source", sa.String(255), nullable=False),
        sa.Column("clinical_verified_by", sa.String(255), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_health_articles_category", "health_articles", ["category"])
    op.execute("CREATE INDEX idx_health_articles_search ON health_articles USING gin(search_vector)")

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("health_articles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_knowledge_chunks_article_id", "knowledge_chunks", ["article_id"])
    op.execute(
        "CREATE INDEX idx_knowledge_chunks_embedding ON knowledge_chunks "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )
    op.execute("CREATE INDEX idx_knowledge_chunks_search ON knowledge_chunks USING gin(search_vector)")

    # 7. PathGuide AI Chat
    op.create_table(
        "pathguide_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(200), server_default="Care Conversation", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_pathguide_threads_user_id", "pathguide_threads", ["user_id"])

    op.create_table(
        "pathguide_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pathguide_threads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("safety_flags", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("tokens_used", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_pathguide_message_role"),
    )
    op.create_index("idx_pathguide_messages_thread_id", "pathguide_messages", ["thread_id"])

    # 8. The Village (Community) & Notifications
    op.create_table(
        "village_channels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("stage_id", sa.Integer(), sa.ForeignKey("journey_stages.id"), nullable=True),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("idx_village_channels_slug", "village_channels", ["slug"])

    op.create_table(
        "village_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("village_channels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_alias", sa.String(100), nullable=False),
        sa.Column("author_avatar_seed", sa.String(100), server_default="avatar1", nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), server_default="published", nullable=False),
        sa.Column("is_flagged", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("upvotes_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("comments_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_village_posts_channel_created", "village_posts", ["channel_id", sa.text("created_at DESC")])
    op.create_index("idx_village_posts_user_id", "village_posts", ["user_id"])

    op.create_table(
        "village_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("village_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_alias", sa.String(100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), server_default="published", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_village_comments_post_id", "village_comments", ["post_id"])

    op.create_table(
        "village_reactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("village_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reaction_type", sa.String(50), server_default="heart", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("post_id", "user_id", "reaction_type", name="uq_village_reaction"),
    )
    op.create_index("idx_village_reactions_post_id", "village_reactions", ["post_id"])

    op.create_table(
        "village_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("reported_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("village_posts.id", ondelete="CASCADE"), nullable=True),
        sa.Column("comment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("village_comments.id", ondelete="CASCADE"), nullable=True),
        sa.Column("reason", sa.String(100), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_village_reports_status", "village_reports", ["status"])

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("action_link", sa.String(500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_notifications_user_unread", "notifications", ["user_id", "is_read", sa.text("scheduled_for DESC")])


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("notifications")
    op.drop_table("village_reports")
    op.drop_table("village_reactions")
    op.drop_table("village_comments")
    op.drop_table("village_posts")
    op.drop_table("village_channels")
    op.drop_table("pathguide_messages")
    op.drop_table("pathguide_threads")
    op.drop_table("knowledge_chunks")
    op.drop_table("health_articles")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("voice_sessions")
    op.drop_table("voice_exercises")
    op.drop_table("appointments")
    op.drop_table("care_team_members")
    op.drop_table("nam_taping_logs")
    op.drop_table("growth_records")
    op.drop_table("feeding_logs")
    op.drop_table("milestone_notes")
    op.drop_table("journey_milestones")
    op.drop_table("journey_stages")
    op.drop_table("patients")
    op.drop_table("audit_logs")
    op.drop_table("consent_records")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS feeding_bottle_type")
    op.execute("DROP TYPE IF EXISTS milestone_status")
    op.execute("DROP TYPE IF EXISTS cleft_alveolus_type")
    op.execute("DROP TYPE IF EXISTS cleft_palate_type")
    op.execute("DROP TYPE IF EXISTS cleft_lip_type")
    op.execute("DROP TYPE IF EXISTS user_role")
