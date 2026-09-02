from datetime import datetime, timezone
import math
from typing import List, Optional
import uuid
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppException
from app.models.notification import Notification
from app.models.user import User, UserRole
from app.models.village import (
    VillageChannel,
    VillageComment,
    VillagePost,
    VillageReaction,
    VillageReport,
)
from app.schemas.village import (
    PaginatedVillageChannelsResponse,
    PaginatedVillageCommentsResponse,
    PaginatedVillagePostsResponse,
    PaginatedVillageReportsResponse,
    VALID_REACTION_TYPES,
    VALID_REPORT_REASONS,
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
from app.services.auth_service import AuthService


class VillageService:
    # ========================================================================
    # Channel Operations
    # ========================================================================

    @classmethod
    async def list_channels(
        cls,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedVillageChannelsResponse:
        """List community channels with post counts."""
        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 50)

        count_res = await db.execute(select(func.count(VillageChannel.id)))
        total_items = count_res.scalar() or 0
        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        # Query channels with posts count
        query = (
            select(VillageChannel, func.count(VillagePost.id).label("posts_count"))
            .outerjoin(VillagePost, (VillagePost.channel_id == VillageChannel.id) & (VillagePost.status == "published"))
            .group_by(VillageChannel.id)
            .order_by(VillageChannel.name.asc())
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(query)
        rows = res.all()

        items = [
            VillageChannelResponse(
                id=channel.id,
                name=channel.name,
                slug=channel.slug,
                description=channel.description,
                stage_id=channel.stage_id,
                is_private=channel.is_private,
                posts_count=p_count,
            )
            for channel, p_count in rows
        ]

        return PaginatedVillageChannelsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
        )

    @classmethod
    async def get_channel_by_id(cls, db: AsyncSession, channel_id: uuid.UUID) -> VillageChannelResponse:
        """Get single channel details."""
        query = (
            select(VillageChannel, func.count(VillagePost.id).label("posts_count"))
            .outerjoin(VillagePost, (VillagePost.channel_id == VillageChannel.id) & (VillagePost.status == "published"))
            .where(VillageChannel.id == channel_id)
            .group_by(VillageChannel.id)
        )
        res = await db.execute(query)
        row = res.first()

        if not row:
            raise AppException(message="Community channel not found.", code="CHANNEL_NOT_FOUND", status_code=404)

        channel, p_count = row
        return VillageChannelResponse(
            id=channel.id,
            name=channel.name,
            slug=channel.slug,
            description=channel.description,
            stage_id=channel.stage_id,
            is_private=channel.is_private,
            posts_count=p_count,
        )

    # ========================================================================
    # Post Operations
    # ========================================================================

    @classmethod
    async def list_posts(
        cls,
        db: AsyncSession,
        current_user: User,
        channel_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedVillagePostsResponse:
        """List published community posts with channel context and user reaction state."""
        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 50)

        # Base filter: only published posts
        filters = [VillagePost.status == "published"]
        if channel_id:
            filters.append(VillagePost.channel_id == channel_id)
        if search and search.strip():
            clean_search = f"%{search.strip()}%"
            filters.append(or_(VillagePost.title.ilike(clean_search), VillagePost.content.ilike(clean_search)))

        count_query = select(func.count(VillagePost.id)).where(*filters)
        count_res = await db.execute(count_query)
        total_items = count_res.scalar() or 0
        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        posts_query = (
            select(VillagePost, VillageChannel)
            .join(VillageChannel, VillagePost.channel_id == VillageChannel.id)
            .where(*filters)
            .order_by(VillagePost.created_at.desc())
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(posts_query)
        rows = res.all()

        post_ids = [post.id for post, _ in rows]

        # Fetch current user reactions for these posts
        user_reactions_map = {}
        if post_ids:
            rx_query = select(VillageReaction).where(
                (VillageReaction.user_id == current_user.id) & (VillageReaction.post_id.in_(post_ids))
            )
            rx_res = await db.execute(rx_query)
            for rx in rx_res.scalars().all():
                user_reactions_map[rx.post_id] = rx.reaction_type

        items = [
            VillagePostResponse(
                id=post.id,
                channel_id=post.channel_id,
                channel_name=channel.name,
                channel_slug=channel.slug,
                user_id=post.user_id,
                author_alias=post.author_alias,
                author_avatar_seed=post.author_avatar_seed,
                title=post.title,
                content=post.content,
                status=post.status,
                is_flagged=post.is_flagged,
                upvotes_count=post.upvotes_count,
                comments_count=post.comments_count,
                has_reacted=post.id in user_reactions_map,
                user_reaction=user_reactions_map.get(post.id),
                created_at=post.created_at,
                updated_at=post.updated_at,
            )
            for post, channel in rows
        ]

        return PaginatedVillagePostsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
        )

    @classmethod
    async def get_post_by_id(
        cls,
        db: AsyncSession,
        post_id: uuid.UUID,
        current_user: User,
    ) -> VillagePostResponse:
        """Get single post details with user reaction status."""
        query = (
            select(VillagePost, VillageChannel)
            .join(VillageChannel, VillagePost.channel_id == VillageChannel.id)
            .where(VillagePost.id == post_id)
        )
        res = await db.execute(query)
        row = res.first()

        if not row:
            raise AppException(message="Post not found.", code="POST_NOT_FOUND", status_code=404)

        post, channel = row

        if post.status != "published" and post.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(message="Post is no longer available.", code="POST_UNAVAILABLE", status_code=404)

        # Check current user reaction
        rx_query = select(VillageReaction).where(
            (VillageReaction.user_id == current_user.id) & (VillageReaction.post_id == post.id)
        )
        rx_res = await db.execute(rx_query)
        rx = rx_res.scalar_one_or_none()

        return VillagePostResponse(
            id=post.id,
            channel_id=post.channel_id,
            channel_name=channel.name,
            channel_slug=channel.slug,
            user_id=post.user_id,
            author_alias=post.author_alias,
            author_avatar_seed=post.author_avatar_seed,
            title=post.title,
            content=post.content,
            status=post.status,
            is_flagged=post.is_flagged,
            upvotes_count=post.upvotes_count,
            comments_count=post.comments_count,
            has_reacted=rx is not None,
            user_reaction=rx.reaction_type if rx else None,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

    @classmethod
    async def create_post(
        cls,
        db: AsyncSession,
        payload: VillagePostCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VillagePostResponse:
        """Create a community post."""
        # 1. Verify channel exists
        ch_res = await db.execute(select(VillageChannel).where(VillageChannel.id == payload.channel_id))
        channel = ch_res.scalar_one_or_none()
        if not channel:
            raise AppException(message="Specified channel does not exist.", code="CHANNEL_NOT_FOUND", status_code=404)

        # 2. Derive safe alias
        alias = payload.author_alias.strip() if payload.author_alias and payload.author_alias.strip() else f"Parent {current_user.first_name}"
        now = datetime.now(timezone.utc)

        new_post = VillagePost(
            id=uuid.uuid4(),
            channel_id=channel.id,
            user_id=current_user.id,
            author_alias=alias[:100],
            author_avatar_seed=payload.author_avatar_seed or "avatar1",
            title=payload.title.strip(),
            content=payload.content.strip(),
            status="published",
            is_flagged=False,
            upvotes_count=0,
            comments_count=0,
            created_at=now,
            updated_at=now,
        )
        db.add(new_post)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VILLAGE_POST_CREATED",
            resource_type="village_post",
            resource_id=str(new_post.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_post_by_id(db, new_post.id, current_user)

    @classmethod
    async def update_post(
        cls,
        db: AsyncSession,
        post_id: uuid.UUID,
        payload: VillagePostUpdateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VillagePostResponse:
        """Update own community post with strict IDOR verification."""
        res = await db.execute(select(VillagePost).where(VillagePost.id == post_id))
        post = res.scalar_one_or_none()

        if not post:
            raise AppException(message="Post not found.", code="POST_NOT_FOUND", status_code=404)

        if post.user_id != current_user.id and current_user.role not in (UserRole.ADMIN, UserRole.CLINICIAN):
            raise AppException(message="Access to edit this post is forbidden.", code="FORBIDDEN", status_code=403)

        if payload.title is not None and payload.title.strip():
            post.title = payload.title.strip()
        if payload.content is not None and payload.content.strip():
            post.content = payload.content.strip()

        post.updated_at = datetime.now(timezone.utc)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VILLAGE_POST_UPDATED",
            resource_type="village_post",
            resource_id=str(post.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return await cls.get_post_by_id(db, post.id, current_user)

    @classmethod
    async def delete_post(
        cls,
        db: AsyncSession,
        post_id: uuid.UUID,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Delete own community post with strict IDOR verification."""
        res = await db.execute(select(VillagePost).where(VillagePost.id == post_id))
        post = res.scalar_one_or_none()

        if not post:
            raise AppException(message="Post not found.", code="POST_NOT_FOUND", status_code=404)

        if post.user_id != current_user.id and current_user.role not in (UserRole.ADMIN, UserRole.CLINICIAN):
            raise AppException(message="Access to delete this post is forbidden.", code="FORBIDDEN", status_code=403)

        await db.delete(post)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VILLAGE_POST_DELETED",
            resource_type="village_post",
            resource_id=str(post_id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

    # ========================================================================
    # Comment Operations
    # ========================================================================

    @classmethod
    async def list_comments(
        cls,
        db: AsyncSession,
        post_id: uuid.UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedVillageCommentsResponse:
        """List comments for a post ordered chronologically."""
        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 100)

        # Check post exists
        post_res = await db.execute(select(VillagePost).where(VillagePost.id == post_id))
        if not post_res.scalar_one_or_none():
            raise AppException(message="Post not found.", code="POST_NOT_FOUND", status_code=404)

        count_query = select(func.count(VillageComment.id)).where(
            (VillageComment.post_id == post_id) & (VillageComment.status == "published")
        )
        count_res = await db.execute(count_query)
        total_items = count_res.scalar() or 0
        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        comments_query = (
            select(VillageComment)
            .where((VillageComment.post_id == post_id) & (VillageComment.status == "published"))
            .order_by(VillageComment.created_at.asc())
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(comments_query)
        comments = res.scalars().all()

        items = [
            VillageCommentResponse(
                id=c.id,
                post_id=c.post_id,
                user_id=c.user_id,
                author_alias=c.author_alias,
                content=c.content,
                status=c.status,
                created_at=c.created_at,
            )
            for c in comments
        ]

        return PaginatedVillageCommentsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
        )

    @classmethod
    async def create_comment(
        cls,
        db: AsyncSession,
        post_id: uuid.UUID,
        payload: VillageCommentCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VillageCommentResponse:
        """Add a comment to a published post."""
        post_res = await db.execute(select(VillagePost).where(VillagePost.id == post_id))
        post = post_res.scalar_one_or_none()

        if not post or post.status != "published":
            raise AppException(message="Post not found or unavailable.", code="POST_NOT_FOUND", status_code=404)

        alias = payload.author_alias.strip() if payload.author_alias and payload.author_alias.strip() else f"Parent {current_user.first_name}"
        now = datetime.now(timezone.utc)

        new_comment = VillageComment(
            id=uuid.uuid4(),
            post_id=post.id,
            user_id=current_user.id,
            author_alias=alias[:100],
            content=payload.content.strip(),
            status="published",
            created_at=now,
        )
        db.add(new_comment)

        # Increment post comment count
        post.comments_count += 1
        await db.flush()

        # Conservative notification for post author (if not commenting on own post)
        if post.user_id != current_user.id:
            db.add(
                Notification(
                    id=uuid.uuid4(),
                    user_id=post.user_id,
                    type="village_comment",
                    title="New response in The Village",
                    body=f"{alias} replied to your post '{post.title[:30]}...'",
                    action_link="/village",
                    created_at=now,
                )
            )

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VILLAGE_COMMENT_CREATED",
            resource_type="village_comment",
            resource_id=str(new_comment.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return VillageCommentResponse(
            id=new_comment.id,
            post_id=new_comment.post_id,
            user_id=new_comment.user_id,
            author_alias=new_comment.author_alias,
            content=new_comment.content,
            status=new_comment.status,
            created_at=new_comment.created_at,
        )

    @classmethod
    async def update_comment(
        cls,
        db: AsyncSession,
        comment_id: uuid.UUID,
        payload: VillageCommentUpdateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VillageCommentResponse:
        """Update own comment with strict IDOR verification."""
        res = await db.execute(select(VillageComment).where(VillageComment.id == comment_id))
        comment = res.scalar_one_or_none()

        if not comment:
            raise AppException(message="Comment not found.", code="COMMENT_NOT_FOUND", status_code=404)

        if comment.user_id != current_user.id and current_user.role not in (UserRole.ADMIN, UserRole.CLINICIAN):
            raise AppException(message="Access to edit this comment is forbidden.", code="FORBIDDEN", status_code=403)

        comment.content = payload.content.strip()
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VILLAGE_COMMENT_UPDATED",
            resource_type="village_comment",
            resource_id=str(comment.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return VillageCommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            user_id=comment.user_id,
            author_alias=comment.author_alias,
            content=comment.content,
            status=comment.status,
            created_at=comment.created_at,
        )

    @classmethod
    async def delete_comment(
        cls,
        db: AsyncSession,
        comment_id: uuid.UUID,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Delete own comment with strict IDOR verification."""
        res = await db.execute(select(VillageComment).where(VillageComment.id == comment_id))
        comment = res.scalar_one_or_none()

        if not comment:
            raise AppException(message="Comment not found.", code="COMMENT_NOT_FOUND", status_code=404)

        if comment.user_id != current_user.id and current_user.role not in (UserRole.ADMIN, UserRole.CLINICIAN):
            raise AppException(message="Access to delete this comment is forbidden.", code="FORBIDDEN", status_code=403)

        post_res = await db.execute(select(VillagePost).where(VillagePost.id == comment.post_id))
        post = post_res.scalar_one_or_none()
        if post and post.comments_count > 0:
            post.comments_count -= 1

        await db.delete(comment)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VILLAGE_COMMENT_DELETED",
            resource_type="village_comment",
            resource_id=str(comment_id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

    # ========================================================================
    # Reaction Operations
    # ========================================================================

    @classmethod
    async def toggle_reaction(
        cls,
        db: AsyncSession,
        post_id: uuid.UUID,
        payload: VillageReactionRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VillageReactionResponse:
        """Toggle reaction (Heart/Hug/Strength) on a post."""
        rx_type = payload.reaction_type.lower().strip()
        if rx_type not in VALID_REACTION_TYPES:
            rx_type = "heart"

        post_res = await db.execute(select(VillagePost).where(VillagePost.id == post_id))
        post = post_res.scalar_one_or_none()

        if not post or post.status != "published":
            raise AppException(message="Post not found or unavailable.", code="POST_NOT_FOUND", status_code=404)

        rx_res = await db.execute(
            select(VillageReaction).where(
                (VillageReaction.post_id == post.id)
                & (VillageReaction.user_id == current_user.id)
                & (VillageReaction.reaction_type == rx_type)
            )
        )
        existing_rx = rx_res.scalar_one_or_none()

        if existing_rx:
            # Remove reaction
            await db.delete(existing_rx)
            if post.upvotes_count > 0:
                post.upvotes_count -= 1
            action = "removed"
            has_reacted = False

            await AuthService.record_audit_log(
                db=db,
                user_id=current_user.id,
                action="VILLAGE_REACTION_REMOVED",
                resource_type="village_reaction",
                resource_id=str(existing_rx.id),
                ip_address=ip_address,
                user_agent=user_agent,
            )
        else:
            # Add reaction
            new_rx = VillageReaction(
                id=uuid.uuid4(),
                post_id=post.id,
                user_id=current_user.id,
                reaction_type=rx_type,
                created_at=datetime.now(timezone.utc),
            )
            db.add(new_rx)
            post.upvotes_count += 1
            action = "added"
            has_reacted = True

            await AuthService.record_audit_log(
                db=db,
                user_id=current_user.id,
                action="VILLAGE_REACTION_ADDED",
                resource_type="village_reaction",
                resource_id=str(new_rx.id),
                ip_address=ip_address,
                user_agent=user_agent,
            )

        await db.flush()
        await db.commit()

        return VillageReactionResponse(
            post_id=post.id,
            reaction_type=rx_type,
            action=action,
            upvotes_count=post.upvotes_count,
            has_reacted=has_reacted,
        )

    # ========================================================================
    # Reporting & Moderation Operations
    # ========================================================================

    @classmethod
    async def create_post_report(
        cls,
        db: AsyncSession,
        post_id: uuid.UUID,
        payload: VillageReportCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VillageReportResponse:
        """Report inappropriate post content."""
        post_res = await db.execute(select(VillagePost).where(VillagePost.id == post_id))
        post = post_res.scalar_one_or_none()

        if not post:
            raise AppException(message="Post not found.", code="POST_NOT_FOUND", status_code=404)

        reason = payload.reason.lower().strip()
        if reason not in VALID_REPORT_REASONS:
            reason = "other"

        new_report = VillageReport(
            id=uuid.uuid4(),
            reported_by_user_id=current_user.id,
            post_id=post.id,
            comment_id=None,
            reason=reason,
            details=payload.details.strip() if payload.details else None,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_report)

        # Count reports on this post
        report_count_res = await db.execute(
            select(func.count(VillageReport.id)).where(VillageReport.post_id == post.id)
        )
        r_count = (report_count_res.scalar() or 0) + 1
        if r_count >= 3:
            post.is_flagged = True

        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VILLAGE_REPORT_CREATED",
            resource_type="village_report",
            resource_id=str(new_report.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return VillageReportResponse(
            id=new_report.id,
            post_id=new_report.post_id,
            comment_id=new_report.comment_id,
            reason=new_report.reason,
            details=new_report.details,
            status=new_report.status,
            created_at=new_report.created_at,
        )

    @classmethod
    async def create_comment_report(
        cls,
        db: AsyncSession,
        comment_id: uuid.UUID,
        payload: VillageReportCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VillageReportResponse:
        """Report inappropriate comment content."""
        comment_res = await db.execute(select(VillageComment).where(VillageComment.id == comment_id))
        comment = comment_res.scalar_one_or_none()

        if not comment:
            raise AppException(message="Comment not found.", code="COMMENT_NOT_FOUND", status_code=404)

        reason = payload.reason.lower().strip()
        if reason not in VALID_REPORT_REASONS:
            reason = "other"

        new_report = VillageReport(
            id=uuid.uuid4(),
            reported_by_user_id=current_user.id,
            post_id=None,
            comment_id=comment.id,
            reason=reason,
            details=payload.details.strip() if payload.details else None,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_report)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VILLAGE_REPORT_CREATED",
            resource_type="village_report",
            resource_id=str(new_report.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return VillageReportResponse(
            id=new_report.id,
            post_id=new_report.post_id,
            comment_id=new_report.comment_id,
            reason=new_report.reason,
            details=new_report.details,
            status=new_report.status,
            created_at=new_report.created_at,
        )

    @classmethod
    async def list_reports(
        cls,
        db: AsyncSession,
        current_user: User,
        status_filter: str = "pending",
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedVillageReportsResponse:
        """Moderation queue: list content reports. Restricted to ADMIN and CLINICIAN."""
        if current_user.role not in (UserRole.ADMIN, UserRole.CLINICIAN):
            raise AppException(message="Access to moderation reports is forbidden.", code="FORBIDDEN", status_code=403)

        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 50)

        filters = []
        if status_filter:
            filters.append(VillageReport.status == status_filter)

        count_query = select(func.count(VillageReport.id))
        if filters:
            count_query = count_query.where(*filters)
        count_res = await db.execute(count_query)
        total_items = count_res.scalar() or 0
        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        query = select(VillageReport).order_by(VillageReport.created_at.desc()).offset(offset).limit(safe_page_size)
        if filters:
            query = query.where(*filters)
        res = await db.execute(query)
        reports = res.scalars().all()

        items = [
            VillageReportResponse(
                id=r.id,
                post_id=r.post_id,
                comment_id=r.comment_id,
                reason=r.reason,
                details=r.details,
                status=r.status,
                created_at=r.created_at,
            )
            for r in reports
        ]

        return PaginatedVillageReportsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
        )

    @classmethod
    async def resolve_report(
        cls,
        db: AsyncSession,
        report_id: uuid.UUID,
        payload: VillageModerationActionRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VillageReportResponse:
        """Moderate reported content. Restricted to ADMIN and CLINICIAN."""
        if current_user.role not in (UserRole.ADMIN, UserRole.CLINICIAN):
            raise AppException(message="Access to moderate content is forbidden.", code="FORBIDDEN", status_code=403)

        res = await db.execute(select(VillageReport).where(VillageReport.id == report_id))
        report = res.scalar_one_or_none()

        if not report:
            raise AppException(message="Report not found.", code="REPORT_NOT_FOUND", status_code=404)

        action = payload.action.lower().strip()
        if action == "hide_content":
            report.status = "resolved"
            if report.post_id:
                p_res = await db.execute(select(VillagePost).where(VillagePost.id == report.post_id))
                post = p_res.scalar_one_or_none()
                if post:
                    post.status = "hidden"
            if report.comment_id:
                c_res = await db.execute(select(VillageComment).where(VillageComment.id == report.comment_id))
                comm = c_res.scalar_one_or_none()
                if comm:
                    comm.status = "hidden"
        elif action == "dismiss":
            report.status = "dismissed"
        else:
            report.status = "resolved"

        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="VILLAGE_REPORT_RESOLVED",
            resource_type="village_report",
            resource_id=str(report.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return VillageReportResponse(
            id=report.id,
            post_id=report.post_id,
            comment_id=report.comment_id,
            reason=report.reason,
            details=report.details,
            status=report.status,
            created_at=report.created_at,
        )
