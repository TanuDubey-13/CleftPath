"""
Tests for development seed data integrity and clinical baseline validity.
"""

from app.db.seed import CLINICAL_STAGES, VILLAGE_CHANNELS, generate_synthetic_embedding


def test_clinical_stages_structure():
    """Verify all 8 ACPA clinical stages are defined with valid keys and hex colors."""
    assert len(CLINICAL_STAGES) == 8
    stage_numbers = [s["stage_number"] for s in CLINICAL_STAGES]
    assert stage_numbers == list(range(8))

    for s in CLINICAL_STAGES:
        assert "title" in s
        assert "age_range_label" in s
        assert "description" in s
        assert s["color_hex"].startswith("#")


def test_village_channels_structure():
    """Verify standard default village channels."""
    assert len(VILLAGE_CHANNELS) == 5
    slugs = [ch["slug"] for ch in VILLAGE_CHANNELS]
    assert "expectant-parents" in slugs
    assert "first-year-feeding" in slugs
    assert "surgery-prep-recovery" in slugs
    assert "speech-and-school" in slugs
    assert "adult-cleft-voices" in slugs


def test_synthetic_embedding_generation():
    """Verify that synthetic embeddings produce 768-dim normalized vectors."""
    emb1 = generate_synthetic_embedding(1.0)
    emb2 = generate_synthetic_embedding(2.0)

    assert len(emb1) == 768
    assert len(emb2) == 768
    assert emb1 != emb2

    # Check vector magnitude is approximately 1.0 (unit vector)
    magnitude = sum(x * x for x in emb1) ** 0.5
    assert abs(magnitude - 1.0) < 0.01
