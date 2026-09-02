from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.health_library import (
    HealthArticleDetailResponse,
    HealthCategoryResponse,
    PaginatedHealthArticlesResponse,
)
from app.services.health_library_service import HealthLibraryService

router = APIRouter()


@router.get(
    "/articles",
    response_model=StandardResponse[PaginatedHealthArticlesResponse],
    status_code=status.HTTP_200_OK,
    summary="List Health Library Articles",
    description="Browse verified cleft healthcare educational articles with pagination, search, category, and stage filtering.",
)
async def list_articles(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search keyword for title, summary, or content"),
    category: Optional[str] = Query(default=None, description="Filter by category name"),
    stage_id: Optional[int] = Query(default=None, description="Filter by journey stage ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PaginatedHealthArticlesResponse]:
    result = await HealthLibraryService.list_articles(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        stage_id=stage_id,
    )
    return StandardResponse(success=True, data=result)


@router.get(
    "/articles/{article_id}",
    response_model=StandardResponse[HealthArticleDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Health Library Article Detail",
    description="Retrieve full markdown content and clinical verification metadata for an educational article by UUID or slug.",
)
async def get_article_detail(
    article_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[HealthArticleDetailResponse]:
    article = await HealthLibraryService.get_article(
        db=db,
        identifier=article_id,
    )
    return StandardResponse(success=True, data=article)


@router.get(
    "/categories",
    response_model=StandardResponse[List[HealthCategoryResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Health Library Categories",
    description="Get list of available article categories with published count tallies.",
)
async def list_categories(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[HealthCategoryResponse]]:
    categories = await HealthLibraryService.get_categories(db=db)
    return StandardResponse(success=True, data=categories)
