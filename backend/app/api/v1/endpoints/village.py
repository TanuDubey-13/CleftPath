from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.village import (
    PaginatedVillageChannelsResponse,
    PaginatedVillageCommentsResponse,
    PaginatedVillagePostsResponse,
    PaginatedVillageReportsResponse,
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

router = APIRouter()


# ============================================================================
# 1. Community Channels
# ============================================================================

@router.get(
    "/channels",
    response_model=StandardResponse[PaginatedVillageChannelsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Community Channels",
)
async def list_channels(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedVillageChannelsResponse]:
    channels = await VillageService.list_channels(db=db, page=page, page_size=page_size)
    return StandardResponse(success=True, data=channels)


@router.get(
    "/channels/{channel_id}",
    response_model=StandardResponse[VillageChannelResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Channel Detail",
)
async def get_channel(
    channel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillageChannelResponse]:
    channel = await VillageService.get_channel_by_id(db=db, channel_id=channel_id)
    return StandardResponse(success=True, data=channel)


@router.get(
    "/channels/{channel_id}/posts",
    response_model=StandardResponse[PaginatedVillagePostsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Posts in Channel",
)
async def list_channel_posts(
    channel_id: uuid.UUID,
    search: Optional[str] = Query(default=None, description="Search keyword"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedVillagePostsResponse]:
    posts = await VillageService.list_posts(
        db=db,
        current_user=current_user,
        channel_id=channel_id,
        search=search,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=posts)


# ============================================================================
# 2. Community Posts
# ============================================================================

@router.get(
    "/posts",
    response_model=StandardResponse[PaginatedVillagePostsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Community Posts",
)
async def list_posts(
    channel_id: Optional[uuid.UUID] = Query(default=None, description="Filter by channel"),
    search: Optional[str] = Query(default=None, description="Search keyword"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedVillagePostsResponse]:
    posts = await VillageService.list_posts(
        db=db,
        current_user=current_user,
        channel_id=channel_id,
        search=search,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=posts)


@router.get(
    "/posts/{post_id}",
    response_model=StandardResponse[VillagePostResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Post Detail",
)
async def get_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillagePostResponse]:
    post = await VillageService.get_post_by_id(db=db, post_id=post_id, current_user=current_user)
    return StandardResponse(success=True, data=post)


@router.post(
    "/posts",
    response_model=StandardResponse[VillagePostResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Community Post",
)
async def create_post(
    payload: VillagePostCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillagePostResponse]:
    post = await VillageService.create_post(
        db=db,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=post)


@router.patch(
    "/posts/{post_id}",
    response_model=StandardResponse[VillagePostResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Community Post",
)
async def update_post(
    post_id: uuid.UUID,
    payload: VillagePostUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillagePostResponse]:
    post = await VillageService.update_post(
        db=db,
        post_id=post_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=post)


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Community Post",
)
async def delete_post(
    post_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await VillageService.delete_post(
        db=db,
        post_id=post_id,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


# ============================================================================
# 3. Post Comments
# ============================================================================

@router.get(
    "/posts/{post_id}/comments",
    response_model=StandardResponse[PaginatedVillageCommentsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Post Comments",
)
async def list_comments(
    post_id: uuid.UUID,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedVillageCommentsResponse]:
    comments = await VillageService.list_comments(
        db=db,
        post_id=post_id,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=comments)


@router.post(
    "/posts/{post_id}/comments",
    response_model=StandardResponse[VillageCommentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Post Comment",
)
async def create_comment(
    post_id: uuid.UUID,
    payload: VillageCommentCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillageCommentResponse]:
    comment = await VillageService.create_comment(
        db=db,
        post_id=post_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=comment)


@router.patch(
    "/comments/{comment_id}",
    response_model=StandardResponse[VillageCommentResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Comment",
)
async def update_comment(
    comment_id: uuid.UUID,
    payload: VillageCommentUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillageCommentResponse]:
    comment = await VillageService.update_comment(
        db=db,
        comment_id=comment_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=comment)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Comment",
)
async def delete_comment(
    comment_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await VillageService.delete_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


# ============================================================================
# 4. Reactions
# ============================================================================

@router.post(
    "/posts/{post_id}/reactions",
    response_model=StandardResponse[VillageReactionResponse],
    status_code=status.HTTP_200_OK,
    summary="Toggle Post Reaction",
)
async def toggle_reaction(
    post_id: uuid.UUID,
    payload: VillageReactionRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillageReactionResponse]:
    reaction = await VillageService.toggle_reaction(
        db=db,
        post_id=post_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=reaction)


# ============================================================================
# 5. Reporting
# ============================================================================

@router.post(
    "/posts/{post_id}/report",
    response_model=StandardResponse[VillageReportResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Report Post",
)
async def report_post(
    post_id: uuid.UUID,
    payload: VillageReportCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillageReportResponse]:
    report = await VillageService.create_post_report(
        db=db,
        post_id=post_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=report)


@router.post(
    "/comments/{comment_id}/report",
    response_model=StandardResponse[VillageReportResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Report Comment",
)
async def report_comment(
    comment_id: uuid.UUID,
    payload: VillageReportCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillageReportResponse]:
    report = await VillageService.create_comment_report(
        db=db,
        comment_id=comment_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=report)


# ============================================================================
# 6. Moderation (Admin / Clinician Only)
# ============================================================================

@router.get(
    "/moderation/reports",
    response_model=StandardResponse[PaginatedVillageReportsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Moderation Reports (Admin/Clinician)",
)
async def list_moderation_reports(
    status_filter: str = Query(default="pending", description="Status filter: pending, resolved, dismissed"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedVillageReportsResponse]:
    reports = await VillageService.list_reports(
        db=db,
        current_user=current_user,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=reports)


@router.post(
    "/moderation/reports/{report_id}/resolve",
    response_model=StandardResponse[VillageReportResponse],
    status_code=status.HTTP_200_OK,
    summary="Resolve Moderation Report (Admin/Clinician)",
)
async def resolve_moderation_report(
    report_id: uuid.UUID,
    payload: VillageModerationActionRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[VillageReportResponse]:
    report = await VillageService.resolve_report(
        db=db,
        report_id=report_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=report)
