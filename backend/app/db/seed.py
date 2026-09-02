"""
CleftPath Development Seed Data Module
Populates safe, purely synthetic test fixtures and baseline clinical datasets.
Zero real patient data. Zero hardcoded production secrets.
"""

import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
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
    VoiceExercise,
    VoiceSession,
)

logger = logging.getLogger("cleftpath.seed")

# Deterministic 768-dimension synthetic embedding vector generator
def generate_synthetic_embedding(seed_val: float) -> list[float]:
    import math
    vec = [math.sin(seed_val * (i + 1) * 0.1) for i in range(768)]
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [round(x / norm, 6) for x in vec]


# Standard 8 ACPA Cleft Care Pathway Stages
CLINICAL_STAGES = [
    {
        "id": 0,
        "stage_number": 0,
        "title": "Stage 0: Prenatal & Diagnosis",
        "age_range_label": "Prenatal",
        "description": "Fetal ultrasound diagnosis, cleft team consultation, prenatal feeding education, and delivery planning.",
        "color_hex": "#0F4C5C",
    },
    {
        "id": 1,
        "stage_number": 1,
        "title": "Stage 1: Infancy & Feeding Setup",
        "age_range_label": "0–3 Months",
        "description": "Specialized bottle feeding, weight velocity monitoring, hearing screen, and presurgical infant orthopedics (NAM).",
        "color_hex": "#81B29A",
    },
    {
        "id": 2,
        "stage_number": 2,
        "title": "Stage 2: Primary Lip Repair",
        "age_range_label": "3–6 Months",
        "description": "Cheiloplasty surgery, primary rhinoplasty, post-op incision care, and arm restraint management.",
        "color_hex": "#E07A5F",
    },
    {
        "id": 3,
        "stage_number": 3,
        "title": "Stage 3: Primary Palate Repair",
        "age_range_label": "9–18 Months",
        "description": "Palatoplasty surgery, tympanostomy ear tube placement, soft food transition, and pre-speech babbling.",
        "color_hex": "#3D5A80",
    },
    {
        "id": 4,
        "stage_number": 4,
        "title": "Stage 4: Early Speech & Dental",
        "age_range_label": "18m–5 Years",
        "description": "Speech-language pathology assessment, velopharyngeal function monitoring, and pediatric dental hygiene.",
        "color_hex": "#2A9D8F",
    },
    {
        "id": 5,
        "stage_number": 5,
        "title": "Stage 5: Bone Graft & Orthodontics",
        "age_range_label": "6–10 Years",
        "description": "Alveolar bone grafting (ABG), canine eruption guidance, maxillary expansion, and phase-1 orthodontic appliances.",
        "color_hex": "#E76F51",
    },
    {
        "id": 6,
        "stage_number": 6,
        "title": "Stage 6: Adolescent & Orthognathic",
        "age_range_label": "11–18 Years",
        "description": "Comprehensive orthodontics, jaw surgery (LeFort osteotomy), revision rhinoplasty, and psychosocial support.",
        "color_hex": "#264653",
    },
    {
        "id": 7,
        "stage_number": 7,
        "title": "Stage 7: Adulthood & Transition",
        "age_range_label": "18+ Years",
        "description": "Transition to adult craniofacial care, final dental prosthetics, speech maintenance, and community advocacy.",
        "color_hex": "#6B705C",
    },
]

VILLAGE_CHANNELS = [
    {
        "name": "Expectant Parents",
        "slug": "expectant-parents",
        "description": "Safe space for families navigating prenatal cleft ultrasound diagnosis and early preparations.",
        "stage_id": 0,
    },
    {
        "name": "First Year Feeding & NAM",
        "slug": "first-year-feeding",
        "description": "Practical discussions on Dr. Brown's, Pigeon, Haberman bottles, weight gain, and NAM taping.",
        "stage_id": 1,
    },
    {
        "name": "Surgery Prep & Recovery",
        "slug": "surgery-prep-recovery",
        "description": "Tips, packing checklists, and care routines for lip repair (3-6m) and palate repair (9-18m).",
        "stage_id": 2,
    },
    {
        "name": "Speech & School Age",
        "slug": "speech-and-school",
        "description": "Speech therapy exercises, school advocacy, and orthodontic journey support.",
        "stage_id": 4,
    },
    {
        "name": "Adult Cleft Voices",
        "slug": "adult-cleft-voices",
        "description": "Community for cleft-affected adults sharing lived experiences, jaw surgery, and advocacy.",
        "stage_id": 7,
    },
]


async def seed_database(session: AsyncSession) -> None:
    """Seed all baseline clinical stages, channels, demo users, patients, and knowledge articles."""
    logger.info("Starting synthetic database seeding...")

    # 1. Seed Journey Stages
    for stage_data in CLINICAL_STAGES:
        res = await session.execute(select(JourneyStage).where(JourneyStage.id == stage_data["id"]))
        if not res.scalar_one_or_none():
            session.add(JourneyStage(**stage_data))
    await session.flush()
    logger.info("Seeded 8 Journey Stages.")

    # 2. Seed Village Channels
    for ch in VILLAGE_CHANNELS:
        res = await session.execute(select(VillageChannel).where(VillageChannel.slug == ch["slug"]))
        if not res.scalar_one_or_none():
            session.add(VillageChannel(id=uuid.uuid4(), **ch))
    await session.flush()
    logger.info("Seeded 5 Village Channels.")

    # 3. Seed Synthetic Demo Users
    # Password hash for synthetic testing: 'demo12345'
    from app.core.security import get_password_hash
    synthetic_hash = get_password_hash("demo12345")

    demo_parent = await session.execute(select(User).where(User.email == "demo.parent@example.com"))
    parent_user = demo_parent.scalar_one_or_none()
    if not parent_user:
        parent_user = User(
            id=uuid.uuid4(),
            email="demo.parent@example.com",
            hashed_password=synthetic_hash,
            first_name="Sarah",
            last_name="DemoParent",
            role=UserRole.CAREGIVER,
            is_active=True,
            is_verified=True,
        )
        session.add(parent_user)
        await session.flush()

        # Consent record
        session.add(
            ConsentRecord(
                id=uuid.uuid4(),
                user_id=parent_user.id,
                terms_version="2026.1",
                privacy_version="2026.1",
                ai_safety_disclaimer_accepted=True,
                data_retention_accepted=True,
                ip_address="127.0.0.1",
            )
        )
    else:
        parent_user.hashed_password = synthetic_hash

    demo_clinician = await session.execute(select(User).where(User.email == "dr.demo@example.com"))
    clinician_user = demo_clinician.scalar_one_or_none()
    if not clinician_user:
        clinician_user = User(
            id=uuid.uuid4(),
            email="dr.demo@example.com",
            hashed_password=synthetic_hash,
            first_name="Robert",
            last_name="Sterling, MD",
            role=UserRole.CLINICIAN,
            is_active=True,
            is_verified=True,
        )
        session.add(clinician_user)
    else:
        clinician_user.hashed_password = synthetic_hash

    await session.flush()
    logger.info("Seeded Demo Users.")

    # 4. Seed Synthetic Demo Patient ("Baby Leo")
    patient_res = await session.execute(select(Patient).where(Patient.user_id == parent_user.id))
    patient = patient_res.scalar_one_or_none()
    if not patient:
        patient = Patient(
            id=uuid.uuid4(),
            user_id=parent_user.id,
            display_name="Baby Leo",
            date_of_birth=date.today() - timedelta(days=120),  # 4 months old
            gender="Male",
            cleft_lip=CleftLipType.UNILATERAL_LEFT_COMPLETE,
            cleft_palate=CleftPalateType.HARD_AND_SOFT_COMPLETE,
            cleft_alveolus=CleftAlveolusType.INVOLVED_LEFT,
            primary_cleft_center="Children's Craniofacial Center",
        )
        session.add(patient)
        await session.flush()

        # Default Milestones for Baby Leo
        milestone1 = JourneyMilestone(
            id=uuid.uuid4(),
            patient_id=patient.id,
            stage_id=1,
            title="Initial Multidisciplinary Cleft Team Evaluation",
            description="Comprehensive visit with plastic surgeon, SLP, pediatric dentist, and otolaryngologist.",
            target_age_months=1,
            status=MilestoneStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc) - timedelta(days=90),
        )
        milestone2 = JourneyMilestone(
            id=uuid.uuid4(),
            patient_id=patient.id,
            stage_id=2,
            title="Primary Lip Repair (Cheiloplasty)",
            description="Surgical restoration of lip symmetry, muscle continuity, and primary nasal tip alignment.",
            target_age_months=4,
            status=MilestoneStatus.IN_PROGRESS,
            target_date=date.today() + timedelta(days=28),
        )
        milestone3 = JourneyMilestone(
            id=uuid.uuid4(),
            patient_id=patient.id,
            stage_id=3,
            title="Primary Palate Repair (Palatoplasty)",
            description="Closure of hard and soft palate and Eustachian tube function evaluation.",
            target_age_months=11,
            status=MilestoneStatus.UPCOMING,
            target_date=date.today() + timedelta(days=210),
        )
        session.add_all([milestone1, milestone2, milestone3])

        # Milestone Note
        session.add(
            MilestoneNote(
                id=uuid.uuid4(),
                milestone_id=milestone1.id,
                user_id=parent_user.id,
                note_text="Dr. Sterling confirmed Leo is gaining weight steadily. Recommended continuing Dr. Brown's feeder.",
            )
        )

        # Care Team Member
        specialist = CareTeamMember(
            id=uuid.uuid4(),
            patient_id=patient.id,
            specialist_name="Dr. Robert Sterling, MD",
            specialty="Plastic & Reconstructive Cleft Surgeon",
            clinic_or_hospital="Children's Craniofacial Center",
            contact_phone="555-019-2834",
            contact_email="dr.sterling.demo@example.com",
            notes="Primary surgeon for cheiloplasty and palatoplasty.",
        )
        session.add(specialist)
        await session.flush()

        # Appointment
        session.add(
            Appointment(
                id=uuid.uuid4(),
                patient_id=patient.id,
                care_team_member_id=specialist.id,
                specialist_name=specialist.specialist_name,
                specialty=specialist.specialty,
                clinic_location="Children's Craniofacial Center, Suite 402",
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=14),
                duration_minutes=45,
                prep_questions=["What is the fasting window before morning surgery?", "Which pain medications are prescribed post-op?"],
                status="scheduled",
            )
        )

        # Feeding Logs
        session.add(
            FeedingLog(
                id=uuid.uuid4(),
                patient_id=patient.id,
                bottle_type=FeedingBottleType.DR_BROWNS_SPECIALTY,
                volume_ml=Decimal("120.00"),
                duration_minutes=25,
                burping_breaks=2,
                reflux_severity="mild",
                notes="Fed upright at 45 degree angle. Finished entire volume comfortably.",
            )
        )

        # Growth Record
        session.add(
            GrowthRecord(
                id=uuid.uuid4(),
                patient_id=patient.id,
                recorded_at=date.today() - timedelta(days=7),
                weight_kg=Decimal("6.200"),
                height_cm=Decimal("62.50"),
                head_circumference_cm=Decimal("41.20"),
                weight_percentile=Decimal("52.00"),
                height_percentile=Decimal("50.00"),
            )
        )

        # NAM Taping Log
        session.add(
            NAMTapingLog(
                id=uuid.uuid4(),
                patient_id=patient.id,
                hours_worn=22,
                appliance_cleaned=True,
                tape_changed=True,
                skin_condition="normal",
                notes="Cleaned appliance with warm sterile water. Cheeks moisturized with barrier film.",
            )
        )

        # Voice Exercise & Session
        voice_ex = VoiceExercise(
            id=uuid.uuid4(),
            title="Infant Bilabial Sound Exploration",
            target_phonemes=["p", "b", "m"],
            stage_id=2,
            prompt_text="Gentle repetitive /pa-pa-pa/ and /ba-ba-ba/ babbling during play.",
            instructions="Maintain direct eye contact and reward any imitation of lip closure sounds.",
            difficulty_level="beginner",
        )
        session.add(voice_ex)
        await session.flush()

        session.add(
            VoiceSession(
                id=uuid.uuid4(),
                patient_id=patient.id,
                exercise_id=voice_ex.id,
                audio_s3_key="synthetic_audio/demo_leo_babble_01.wav",
                duration_seconds=45,
                repetition_count=3,
                dsp_features_json={"rms_energy": 0.042, "fundamental_freq_hz": 310.5},
                parent_notes="Leo laughed and produced two clear /ba/ vocalizations.",
            )
        )

    logger.info("Seeded Demo Patient & Clinical Records.")

    # 5. Seed Health Library Articles & pgvector Knowledge Chunks
    article_res = await session.execute(
        select(HealthArticle).where(HealthArticle.slug == "understanding-specialized-cleft-feeders")
    )
    if not article_res.scalar_one_or_none():
        article1 = HealthArticle(
            id=uuid.uuid4(),
            title="Understanding Specialized Cleft Feeders: Dr. Brown's vs Pigeon vs Haberman",
            slug="understanding-specialized-cleft-feeders",
            category="Feeding & Nutrition",
            stage_id=1,
            summary="A comprehensive clinical comparison of unidirectional valves, flow rates, and assisted squeezing techniques for cleft palate infants.",
            content_markdown="""# Understanding Specialized Cleft Feeders

Infants born with an intact secondary palate generate negative intraoral suction to draw milk. Because a cleft palate prevents negative pressure seal, specialized feeding systems utilize positive pressure and one-way valves.

### 1. Dr. Brown's Specialty Feeding System
* **Mechanism:** Blue Infant-Paced Feeding Valve inserted into standard Dr. Brown's bottle.
* **Advantage:** Familiar look, dishwasher safe, standard nipple levels.

### 2. Pigeon Cleft Palate Nipple & Bottle
* **Mechanism:** One-way valve with dual-density silicone nipple (stiff top, soft underside).
* **Advantage:** Baby compresses nipple against maxillary ridge without parent squeezing.

### 3. Medela SpecialNeeds (Haberman) Feeder
* **Mechanism:** Slit-valve with 3 adjustable line settings for parent-assisted compression.
* **Advantage:** Helpful for infants with low tone or severe retrognathia.
""",
            author_source="ACPA Family Resources & Guidelines",
            clinical_verified_by="Pediatric Cleft Nutrition Council",
            is_published=True,
            version=1,
        )
        session.add(article1)
        await session.flush()

        # Add 768-dim knowledge chunks
        chunk1 = KnowledgeChunk(
            id=uuid.uuid4(),
            article_id=article1.id,
            chunk_index=0,
            content="Specialized cleft feeders use positive pressure and one-way valves because cleft palate infants cannot create negative suction. Systems include Dr. Brown's Specialty Feeder, Pigeon Cleft Feeder, and Medela SpecialNeeds.",
            embedding=generate_synthetic_embedding(1.0),
            metadata_json={"category": "Feeding & Nutrition", "stage": 1, "article_slug": article1.slug},
        )
        chunk2 = KnowledgeChunk(
            id=uuid.uuid4(),
            article_id=article1.id,
            chunk_index=1,
            content="When feeding with Dr. Brown's Specialty Feeder, keep the infant seated at a 45-degree upright angle to prevent nasopharyngeal reflux and facilitate gravitational flow.",
            embedding=generate_synthetic_embedding(2.0),
            metadata_json={"category": "Feeding & Nutrition", "stage": 1, "article_slug": article1.slug},
        )
        session.add_all([chunk1, chunk2])

    # Article 2: Surgery Prep
    art2_res = await session.execute(
        select(HealthArticle).where(HealthArticle.slug == "preparing-for-primary-lip-repair")
    )
    if not art2_res.scalar_one_or_none():
        article2 = HealthArticle(
            id=uuid.uuid4(),
            title="Preparing for Primary Lip Repair (Cheiloplasty): What Parents Should Expect",
            slug="preparing-for-primary-lip-repair",
            category="Surgery Prep & Recovery",
            stage_id=2,
            summary="Essential pre-operative instructions, surgical timeline, fasting guidelines, and post-operative arm restraint recovery routines for infant lip repair.",
            content_markdown="""# Preparing for Primary Lip Repair (Cheiloplasty)

Primary lip repair (cheiloplasty) is typically scheduled between 3 and 6 months of age, once your baby achieves steady weight gain and clearance from pediatric anesthesia.

### Pre-Surgical Checklist
* **Fasting Guidelines:** Adhere strictly to the hospital's NPO (nothing by mouth) window for breast milk, formula, or clear liquids.
* **Health Check:** Contact the cleft surgical coordinator if your baby develops a fever, cough, or congestion in the 7 days preceding surgery.
* **Packing Essentials:** Bring button-front or zippered shirts (to avoid pulling clothing over the head), your specialized feeder, and soothing comfort blankets.

### Post-Operative Care
* **Incision Care:** Gently clean incision lines with sterile saline using a soft cotton applicator as directed by your surgeon.
* **Arm Restraints (No-No's):** Soft elbow immobilizers prevent babies from touching surgical sutures while allowing full shoulder movement.
""",
            author_source="American Cleft Palate-Craniofacial Association (ACPA)",
            clinical_verified_by="Pediatric Craniofacial Surgical Committee",
            is_published=True,
            version=1,
        )
        session.add(article2)

    # Article 3: Speech
    art3_res = await session.execute(
        select(HealthArticle).where(HealthArticle.slug == "early-speech-sound-development")
    )
    if not art3_res.scalar_one_or_none():
        article3 = HealthArticle(
            id=uuid.uuid4(),
            title="Early Speech Sound Development: Nurturing Vocalizations in Cleft Palate Infants",
            slug="early-speech-sound-development",
            category="Speech & Development",
            stage_id=4,
            summary="Guidance for parents on encouraging pressure consonant babbling, monitoring nasal resonance, and early speech-language therapy milestones.",
            content_markdown="""# Early Speech Sound Development

Before palate repair surgery, infants cannot generate high intraoral air pressure required for plosive sounds like /p/, /b/, /t/, and /d/. Nasal consonants like /m/ and /n/ and vowel sounds predominate early vocalizations.

### Practical Communication Strategies
* **Face-to-Face Babble Play:** Imitate your child's vocalizations, emphasizing lip sounds (/ba/, /ma/, /pa/) during reciprocal play.
* **Language Enrichment:** Label everyday items, read books with repetitive sound patterns, and reinforce early gestures.
* **Monitoring Hearing:** Middle ear fluid (otitis media with effusion) is common with cleft palate. Consistent audiological assessments ensure clear auditory input for speech acquisition.
""",
            author_source="Cleft Palate Speech-Language Pathology Guidelines",
            clinical_verified_by="Speech-Language Pathology Clinical Advisory",
            is_published=True,
            version=1,
        )
        session.add(article3)

    # Article 4: Orthodontics / NAM
    art4_res = await session.execute(
        select(HealthArticle).where(HealthArticle.slug == "caring-for-nam-appliance")
    )
    if not art4_res.scalar_one_or_none():
        article4 = HealthArticle(
            id=uuid.uuid4(),
            title="Presurgical Infant Orthopedics: Caring for the NAM Appliance",
            slug="caring-for-nam-appliance",
            category="Orthodontics & Dental",
            stage_id=1,
            summary="Step-by-step instructions for cleaning Nasoalveolar Molding (NAM) plates, skin protection techniques for tape adhesives, and adjustment visit timelines.",
            content_markdown="""# Presurgical Infant Orthopedics: Caring for the NAM Appliance

Nasoalveolar Molding (NAM) gently approximates the alveolar cleft segments and aligns nasal cartilage before primary lip repair.

### Daily Appliance Hygiene
1. **Cleaning:** Clean the acrylic molding plate twice daily with cool or lukewarm water and a soft-bristled baby toothbrush. Never use boiling water or harsh chemicals.
2. **Skin Barrier Film:** Apply non-alcohol skin barrier wipes to baby's cheeks before placing retention tapes to protect delicate infant skin.
3. **Tape Tension:** Verify that elastic tension matches the orthodontist's prescribed caliper calibration.
""",
            author_source="Craniofacial Orthodontic Protocol Series",
            clinical_verified_by="Pediatric Craniofacial Orthodontics Team",
            is_published=True,
            version=1,
        )
        session.add(article4)

    await session.commit()
    logger.info("Synthetic database seeding completed successfully.")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async with AsyncSessionLocal() as session:
        await seed_database(session)


if __name__ == "__main__":
    asyncio.run(main())
