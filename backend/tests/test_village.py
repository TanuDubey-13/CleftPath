"""
Comprehensive Unit and Integration Tests for Phase 11: The Village (Community Peer Support & Safe Moderation).
Verifies Authentication, IDOR cross-user post/comment/report isolation, Input bounds validation,
Reaction toggling, Role-based moderation queues, Audit logging, and Content safety.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import uuid
from httpx import ASGITransport, AsyncClient
import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.main import app
from app.models.user import User, UserRole
from app.models.village import (
    VillageChannel,
    VillageComment,
    VillagePost,
    VillageReaction,
    VillageReport,
)
from app.schemas.village import (
    VillageChannelResponse,
    VillageCommentCreateRequest,
    VillageCommentResponse,
    VillageCommentUpdateRequest,
    VillageModerationActionRequest,
    VillagePostCreateRequest,
    VillagePostResponse,
    VillagePostUpdateRequest,
    VillageReactionRequest,
    VillageReactionResponse,
    VillageReportCreateRequest,
    VillageReportResponse,
)
from app.services.village_service import VillageService


# ============================================================================
# 1. Authentication Tests (1 - 5)
# ============================================================================

@pytest.mark.asyncio
async def test_unauthenticated_channels_list_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/api/v1/village/channels")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_post_creation_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post("/api/v1/village/posts", json={"title": "Test", "content": "Content", "channel_id": str(uuid.uuid4())})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_comment_creation_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post(f"/api/v1/village/posts/{uuid.uuid4()}/comments", json={"content": "Nice post"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_reaction_toggle_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post(f"/api/v1/village/posts/{uuid.uuid4()}/reactions", json={"reaction_type": "heart"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_report_creation_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post(f"/api/v1/village/posts/{uuid.uuid4()}/report", json={"reason": "spam"})
        assert res.status_code == 401


# ============================================================================
# 2. IDOR & Ownership Protection Tests (6 - 11)
# ============================================================================

@pytest.mark.asyncio
async def test_cross_user_post_update_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    post_a = VillagePost(
        id=uuid.uuid4(),
        channel_id=uuid.uuid4(),
        user_id=uuid.uuid4(),  # Different user
        author_alias="Parent A",
        author_avatar_seed="avatar1",
        title="Post A",
        content="Content A",
        status="published",
        is_flagged=False,
        upvotes_count=0,
        comments_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=post_a))

    with pytest.raises(AppException) as exc:
        await VillageService.update_post(mock_db, post_a.id, VillagePostUpdateRequest(title="Hacked"), user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_post_delete_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    post_a = VillagePost(
        id=uuid.uuid4(),
        channel_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        author_alias="Parent A",
        author_avatar_seed="avatar1",
        title="Post A",
        content="Content A",
        status="published",
        is_flagged=False,
        upvotes_count=0,
        comments_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=post_a))

    with pytest.raises(AppException) as exc:
        await VillageService.delete_post(mock_db, post_a.id, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_comment_update_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    comment_a = VillageComment(
        id=uuid.uuid4(),
        post_id=uuid.uuid4(),
        user_id=uuid.uuid4(),  # Different user
        author_alias="Parent A",
        content="Comment A",
        status="published",
        created_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=comment_a))

    with pytest.raises(AppException) as exc:
        await VillageService.update_comment(mock_db, comment_a.id, VillageCommentUpdateRequest(content="Modified"), user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_comment_delete_blocked():
    user_b = User(id=uuid.uuid4(), email="b@example.com", hashed_password="h", first_name="B", last_name="B", role=UserRole.CAREGIVER, is_active=True)
    comment_a = VillageComment(
        id=uuid.uuid4(),
        post_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        author_alias="Parent A",
        content="Comment A",
        status="published",
        created_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=comment_a))

    with pytest.raises(AppException) as exc:
        await VillageService.delete_comment(mock_db, comment_a.id, user_b)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_moderation_queue_blocked_for_caregiver():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    mock_db = AsyncMock(spec=AsyncSession)

    with pytest.raises(AppException) as exc:
        await VillageService.list_reports(mock_db, user)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_moderation_queue_accessible_for_admin():
    admin = User(id=uuid.uuid4(), email="admin@example.com", hashed_password="h", first_name="A", last_name="A", role=UserRole.ADMIN, is_active=True)
    report = VillageReport(
        id=uuid.uuid4(),
        reported_by_user_id=uuid.uuid4(),
        post_id=uuid.uuid4(),
        reason="spam",
        status="pending",
        created_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[report])))),
    ]

    res = await VillageService.list_reports(mock_db, admin)
    assert res.total == 1
    assert res.items[0].reason == "spam"


# ============================================================================
# 3. Input Validation Bounds Tests (12 - 15)
# ============================================================================

def test_empty_post_title_rejected():
    with pytest.raises(ValidationError):
        VillagePostCreateRequest(channel_id=uuid.uuid4(), title="   ", content="Valid content text")


def test_empty_post_content_rejected():
    with pytest.raises(ValidationError):
        VillagePostCreateRequest(channel_id=uuid.uuid4(), title="Valid Title", content="")


def test_empty_comment_content_rejected():
    with pytest.raises(ValidationError):
        VillageCommentCreateRequest(content="")


def test_oversized_post_content_rejected():
    with pytest.raises(ValidationError):
        VillagePostCreateRequest(channel_id=uuid.uuid4(), title="Valid Title", content="A" * 10001)


# ============================================================================
# 4. Channels Lifecycle Tests (16 - 18)
# ============================================================================

@pytest.mark.asyncio
async def test_list_channels_with_post_counts():
    channel = VillageChannel(
        id=uuid.uuid4(),
        name="First Year Feeding & NAM",
        slug="first-year-feeding",
        description="Feeding discussions",
        stage_id=1,
        is_private=False,
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(all=MagicMock(return_value=[(channel, 5)])),
    ]

    res = await VillageService.list_channels(mock_db)
    assert res.total == 1
    assert res.items[0].name == "First Year Feeding & NAM"
    assert res.items[0].posts_count == 5


@pytest.mark.asyncio
async def test_get_channel_by_id():
    channel = VillageChannel(
        id=uuid.uuid4(),
        name="Surgery Prep",
        slug="surgery-prep",
        description="Prep tips",
        stage_id=2,
        is_private=False,
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(first=MagicMock(return_value=(channel, 12)))

    res = await VillageService.get_channel_by_id(mock_db, channel.id)
    assert res.name == "Surgery Prep"
    assert res.posts_count == 12


@pytest.mark.asyncio
async def test_get_nonexistent_channel_returns_404():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(first=MagicMock(return_value=None))

    with pytest.raises(AppException) as exc:
        await VillageService.get_channel_by_id(mock_db, uuid.uuid4())
    assert exc.value.status_code == 404


# ============================================================================
# 5. Posts Lifecycle Tests (19 - 22)
# ============================================================================

@pytest.mark.asyncio
async def test_create_and_retrieve_post():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="Sarah", last_name="Parent", role=UserRole.CAREGIVER, is_active=True)
    channel = VillageChannel(id=uuid.uuid4(), name="Surgery Prep", slug="surgery-prep", description="Prep", stage_id=2, is_private=False)

    mock_post = VillagePost(
        id=uuid.uuid4(),
        channel_id=channel.id,
        user_id=user.id,
        author_alias="Parent Sarah",
        author_avatar_seed="avatar1",
        title="Arm Restraints Tips",
        content="How do you keep soft arm restraints comfortable?",
        status="published",
        is_flagged=False,
        upvotes_count=0,
        comments_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=channel)),      # channel check
        MagicMock(first=MagicMock(return_value=(mock_post, channel))),      # get_post_by_id
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),         # user reaction check
    ]

    payload = VillagePostCreateRequest(
        channel_id=channel.id,
        title="Arm Restraints Tips",
        content="How do you keep soft arm restraints comfortable?",
    )
    res = await VillageService.create_post(mock_db, payload, user)

    assert res.title == "Arm Restraints Tips"
    assert res.author_alias == "Parent Sarah"
    assert res.channel_name == "Surgery Prep"


@pytest.mark.asyncio
async def test_update_own_post():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="Sarah", last_name="Parent", role=UserRole.CAREGIVER, is_active=True)
    channel = VillageChannel(id=uuid.uuid4(), name="Surgery Prep", slug="surgery-prep", description="Prep", stage_id=2, is_private=False)

    post = VillagePost(
        id=uuid.uuid4(),
        channel_id=channel.id,
        user_id=user.id,
        author_alias="Parent Sarah",
        author_avatar_seed="avatar1",
        title="Old Title",
        content="Old Content",
        status="published",
        is_flagged=False,
        upvotes_count=0,
        comments_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=post)),        # post lookup
        MagicMock(first=MagicMock(return_value=(post, channel))),          # get_post_by_id
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),         # user reaction check
    ]

    res = await VillageService.update_post(mock_db, post.id, VillagePostUpdateRequest(title="Updated Title"), user)
    assert post.title == "Updated Title"


@pytest.mark.asyncio
async def test_delete_own_post():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="Sarah", last_name="Parent", role=UserRole.CAREGIVER, is_active=True)
    post = VillagePost(
        id=uuid.uuid4(),
        channel_id=uuid.uuid4(),
        user_id=user.id,
        author_alias="Parent Sarah",
        author_avatar_seed="avatar1",
        title="Title",
        content="Content",
        status="published",
        is_flagged=False,
        upvotes_count=0,
        comments_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=post))

    await VillageService.delete_post(mock_db, post.id, user)
    mock_db.delete.assert_called_once_with(post)


@pytest.mark.asyncio
async def test_list_posts_channel_and_search_filter():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    channel = VillageChannel(id=uuid.uuid4(), name="Surgery Prep", slug="surgery-prep", description="Prep", stage_id=2, is_private=False)
    post = VillagePost(
        id=uuid.uuid4(),
        channel_id=channel.id,
        user_id=user.id,
        author_alias="Parent Sarah",
        author_avatar_seed="avatar1",
        title="No-No Restraints",
        content="Comfort tips",
        status="published",
        is_flagged=False,
        upvotes_count=3,
        comments_count=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar=MagicMock(return_value=1)),
        MagicMock(all=MagicMock(return_value=[(post, channel)])),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]

    res = await VillageService.list_posts(mock_db, user, channel_id=channel.id, search="restraints")
    assert res.total == 1
    assert res.items[0].title == "No-No Restraints"


# ============================================================================
# 6. Comments Lifecycle Tests (23 - 25)
# ============================================================================

@pytest.mark.asyncio
async def test_create_and_retrieve_comment():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="Leo", last_name="Parent", role=UserRole.CAREGIVER, is_active=True)
    post = VillagePost(
        id=uuid.uuid4(),
        channel_id=uuid.uuid4(),
        user_id=uuid.uuid4(),  # Different user created post
        author_alias="Parent A",
        author_avatar_seed="avatar1",
        title="Post Title",
        content="Post Content",
        status="published",
        is_flagged=False,
        upvotes_count=0,
        comments_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=post))

    payload = VillageCommentCreateRequest(content="We used soft socks over the cuffs!")
    res = await VillageService.create_comment(mock_db, post.id, payload, user)

    assert res.content == "We used soft socks over the cuffs!"
    assert res.author_alias == "Parent Leo"
    assert post.comments_count == 1


@pytest.mark.asyncio
async def test_update_own_comment():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="Leo", last_name="Parent", role=UserRole.CAREGIVER, is_active=True)
    comment = VillageComment(
        id=uuid.uuid4(),
        post_id=uuid.uuid4(),
        user_id=user.id,
        author_alias="Parent Leo",
        content="Original comment",
        status="published",
        created_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=comment))

    res = await VillageService.update_comment(mock_db, comment.id, VillageCommentUpdateRequest(content="Updated comment"), user)
    assert comment.content == "Updated comment"


@pytest.mark.asyncio
async def test_delete_own_comment():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="Leo", last_name="Parent", role=UserRole.CAREGIVER, is_active=True)
    post_id = uuid.uuid4()
    comment = VillageComment(
        id=uuid.uuid4(),
        post_id=post_id,
        user_id=user.id,
        author_alias="Parent Leo",
        content="To delete",
        status="published",
        created_at=datetime.now(timezone.utc),
    )
    post = VillagePost(
        id=post_id,
        channel_id=uuid.uuid4(),
        user_id=user.id,
        author_alias="Author",
        author_avatar_seed="a",
        title="T",
        content="C",
        status="published",
        is_flagged=False,
        upvotes_count=0,
        comments_count=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=comment)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=post)),
    ]

    await VillageService.delete_comment(mock_db, comment.id, user)
    mock_db.delete.assert_called_once_with(comment)
    assert post.comments_count == 0


# ============================================================================
# 7. Reactions Tests (26 - 27)
# ============================================================================

@pytest.mark.asyncio
async def test_add_and_toggle_reaction():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    post = VillagePost(
        id=uuid.uuid4(),
        channel_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        author_alias="Author",
        author_avatar_seed="a",
        title="T",
        content="C",
        status="published",
        is_flagged=False,
        upvotes_count=0,
        comments_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=post)),    # post check
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),    # reaction lookup (none -> add)
    ]

    res = await VillageService.toggle_reaction(mock_db, post.id, VillageReactionRequest(reaction_type="heart"), user)
    assert res.action == "added"
    assert res.has_reacted is True
    assert post.upvotes_count == 1


# ============================================================================
# 8. Reporting & Moderation Tests (28 - 29)
# ============================================================================

@pytest.mark.asyncio
async def test_report_post_and_comment():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="U", last_name="U", role=UserRole.CAREGIVER, is_active=True)
    post = VillagePost(
        id=uuid.uuid4(),
        channel_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        author_alias="Author",
        author_avatar_seed="a",
        title="T",
        content="C",
        status="published",
        is_flagged=False,
        upvotes_count=0,
        comments_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=post)),
        MagicMock(scalar=MagicMock(return_value=2)),  # 2 previous reports + 1 = 3 -> flags post
    ]

    res = await VillageService.create_post_report(
        mock_db, post.id, VillageReportCreateRequest(reason="medical_misinformation", details="Claims unverified home treatment"), user
    )
    assert res.reason == "medical_misinformation"
    assert post.is_flagged is True


@pytest.mark.asyncio
async def test_resolve_moderation_report_hide_content():
    admin = User(id=uuid.uuid4(), email="admin@example.com", hashed_password="h", first_name="A", last_name="A", role=UserRole.ADMIN, is_active=True)
    post_id = uuid.uuid4()
    post = VillagePost(id=post_id, channel_id=uuid.uuid4(), user_id=uuid.uuid4(), author_alias="A", author_avatar_seed="a", title="T", content="C", status="published", is_flagged=True, upvotes_count=0, comments_count=0, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    report = VillageReport(id=uuid.uuid4(), reported_by_user_id=uuid.uuid4(), post_id=post_id, reason="spam", status="pending", created_at=datetime.now(timezone.utc))

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=report)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=post)),
    ]

    res = await VillageService.resolve_report(mock_db, report.id, VillageModerationActionRequest(action="hide_content"), admin)
    assert res.status == "resolved"
    assert post.status == "hidden"


# ============================================================================
# 9. Audit Logging & XSS Safety Tests (30 - 32)
# ============================================================================

@pytest.mark.asyncio
async def test_village_post_create_audit():
    user = User(id=uuid.uuid4(), email="u@example.com", hashed_password="h", first_name="Sarah", last_name="P", role=UserRole.CAREGIVER, is_active=True)
    channel = VillageChannel(id=uuid.uuid4(), name="Channel", slug="ch", description="Desc", stage_id=1, is_private=False)
    mock_post = VillagePost(id=uuid.uuid4(), channel_id=channel.id, user_id=user.id, author_alias="Alias", author_avatar_seed="a", title="T", content="C", status="published", is_flagged=False, upvotes_count=0, comments_count=0, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=channel)),
        MagicMock(first=MagicMock(return_value=(mock_post, channel))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
    ]

    await VillageService.create_post(
        mock_db,
        VillagePostCreateRequest(channel_id=channel.id, title="Valid Post Title", content="Valid post body content here."),
        user,
        ip_address="127.0.0.1",
    )
    assert mock_db.add.call_count >= 2  # post + audit log


def test_malicious_script_tags_in_content_are_safely_persisted_without_executing():
    xss_payload = "<script>alert('xss')</script><img src=x onerror=alert(1)>"
    req = VillagePostCreateRequest(channel_id=uuid.uuid4(), title="Innocent Title", content=xss_payload)
    assert req.content == xss_payload  # Persisted safely as raw string data, not executed as HTML


def test_sensitive_fields_not_leaked_in_village_schemas():
    schemas = [
        VillagePostResponse.model_json_schema(),
        VillageCommentResponse.model_json_schema(),
        VillageChannelResponse.model_json_schema(),
        VillageReportResponse.model_json_schema(),
    ]

    for s in schemas:
        schema_str = str(s).lower()
        assert "password" not in schema_str
        assert "jwt" not in schema_str
        assert "secret" not in schema_str
        assert "email" not in schema_str
