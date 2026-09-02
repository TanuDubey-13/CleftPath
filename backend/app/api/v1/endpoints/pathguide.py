from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.pathguide import (
    PaginatedPathGuideMessagesResponse,
    PaginatedPathGuideThreadsResponse,
    PathGuideMessageCreateRequest,
    PathGuideMessageResponse,
    PathGuideSuggestedPromptsResponse,
    PathGuideThreadCreateRequest,
    PathGuideThreadResponse,
    PathGuideThreadUpdateRequest,
)
from app.services.pathguide_service import PathGuideService

router = APIRouter()


# ============================================================================
# 1. Suggested Prompts
# ============================================================================

@router.get(
    "/suggested-prompts",
    response_model=StandardResponse[PathGuideSuggestedPromptsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Educational Starter Prompts",
)
async def get_suggested_prompts(
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[PathGuideSuggestedPromptsResponse]:
    prompts = PathGuideService.get_suggested_prompts()
    return StandardResponse(success=True, data=prompts)


# ============================================================================
# 2. Conversation Threads
# ============================================================================

@router.get(
    "/threads",
    response_model=StandardResponse[PaginatedPathGuideThreadsResponse],
    status_code=status.HTTP_200_OK,
    summary="List Conversation Threads",
)
async def list_threads(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedPathGuideThreadsResponse]:
    threads = await PathGuideService.list_threads(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=threads)


@router.post(
    "/threads",
    response_model=StandardResponse[PathGuideThreadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Conversation Thread",
)
async def create_thread(
    payload: PathGuideThreadCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PathGuideThreadResponse]:
    thread = await PathGuideService.create_thread(
        db=db,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=thread)


@router.get(
    "/threads/{thread_id}",
    response_model=StandardResponse[PathGuideThreadResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Conversation Thread Detail",
)
async def get_thread(
    thread_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PathGuideThreadResponse]:
    thread = await PathGuideService.get_thread_by_id(
        db=db,
        thread_id=thread_id,
        current_user=current_user,
    )
    return StandardResponse(success=True, data=thread)


@router.patch(
    "/threads/{thread_id}",
    response_model=StandardResponse[PathGuideThreadResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Conversation Thread",
)
async def update_thread(
    thread_id: uuid.UUID,
    payload: PathGuideThreadUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PathGuideThreadResponse]:
    thread = await PathGuideService.update_thread(
        db=db,
        thread_id=thread_id,
        payload=payload,
        current_user=current_user,
    )
    return StandardResponse(success=True, data=thread)


@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Conversation Thread",
)
async def delete_thread(
    thread_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await PathGuideService.delete_thread(
        db=db,
        thread_id=thread_id,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


# ============================================================================
# 3. Messages & Grounded Generation
# ============================================================================

@router.get(
    "/threads/{thread_id}/messages",
    response_model=StandardResponse[PaginatedPathGuideMessagesResponse],
    status_code=status.HTTP_200_OK,
    summary="List Thread Messages",
)
async def list_messages(
    thread_id: uuid.UUID,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedPathGuideMessagesResponse]:
    messages = await PathGuideService.list_messages(
        db=db,
        thread_id=thread_id,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )
    return StandardResponse(success=True, data=messages)


@router.post(
    "/threads/{thread_id}/messages",
    response_model=StandardResponse[PathGuideMessageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send Message to PathGuide",
    description="Ask a question to PathGuide, retrieve grounded knowledge citations, and receive an educational AI response.",
)
async def create_message(
    thread_id: uuid.UUID,
    payload: PathGuideMessageCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PathGuideMessageResponse]:
    response = await PathGuideService.create_message(
        db=db,
        thread_id=thread_id,
        payload=payload,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return StandardResponse(success=True, data=response)
