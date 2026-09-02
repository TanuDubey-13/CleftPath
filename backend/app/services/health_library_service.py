import math
from typing import List, Optional
import uuid
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppException
from app.models.knowledge import HealthArticle
from app.schemas.health_library import (
    HealthArticleCardResponse,
    HealthArticleDetailResponse,
    HealthCategoryResponse,
    PaginatedHealthArticlesResponse,
    calculate_reading_time,
)


class HealthLibraryService:
    @classmethod
    async def list_articles(
        cls,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        stage_id: Optional[int] = None,
    ) -> PaginatedHealthArticlesResponse:
        """List published health library articles with search, category filters, and pagination."""
        # Normalize and validate pagination parameters
        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 100)

        # Base filter: strictly published content only
        filters = [HealthArticle.is_published.is_(True)]

        # Search filter across title, summary, and markdown content
        if search and search.strip():
            clean_search = f"%{search.strip()}%"
            filters.append(
                or_(
                    HealthArticle.title.ilike(clean_search),
                    HealthArticle.summary.ilike(clean_search),
                    HealthArticle.content_markdown.ilike(clean_search),
                )
            )

        # Category filter
        if category and category.strip() and category.strip().lower() != "all":
            filters.append(HealthArticle.category == category.strip())

        # Stage filter
        if stage_id is not None:
            filters.append(HealthArticle.stage_id == stage_id)

        # Count total matching items
        count_query = select(func.count(HealthArticle.id)).where(*filters)
        count_res = await db.execute(count_query)
        total_items = count_res.scalar() or 0

        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        # Query paginated rows with stage eager loading
        query = (
            select(HealthArticle)
            .where(*filters)
            .options(selectinload(HealthArticle.stage))
            .order_by(HealthArticle.created_at.desc(), HealthArticle.title.asc())
            .offset(offset)
            .limit(safe_page_size)
        )
        articles_res = await db.execute(query)
        articles = articles_res.scalars().all()

        card_responses = [
            HealthArticleCardResponse(
                id=art.id,
                slug=art.slug,
                title=art.title,
                category=art.category,
                stage_id=art.stage_id,
                stage_title=art.stage.title if art.stage else None,
                summary=art.summary,
                author_source=art.author_source,
                clinical_verified_by=art.clinical_verified_by,
                reading_time_minutes=calculate_reading_time(art.content_markdown),
                created_at=art.created_at,
                updated_at=art.updated_at,
            )
            for art in articles
        ]

        return PaginatedHealthArticlesResponse(
            items=card_responses,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
        )

    @classmethod
    async def get_article(
        cls,
        db: AsyncSession,
        identifier: str,
    ) -> HealthArticleDetailResponse:
        """Fetch complete educational article by UUID or slug, ensuring published status."""
        filters = [HealthArticle.is_published.is_(True)]

        try:
            art_uuid = uuid.UUID(identifier)
            filters.append(HealthArticle.id == art_uuid)
        except ValueError:
            filters.append(HealthArticle.slug == identifier.strip())

        query = (
            select(HealthArticle)
            .where(*filters)
            .options(selectinload(HealthArticle.stage))
        )
        res = await db.execute(query)
        article = res.scalar_one_or_none()

        if not article:
            raise AppException(
                message="Health educational article not found.",
                code="ARTICLE_NOT_FOUND",
                status_code=404,
            )

        return HealthArticleDetailResponse(
            id=article.id,
            slug=article.slug,
            title=article.title,
            category=article.category,
            stage_id=article.stage_id,
            stage_title=article.stage.title if article.stage else None,
            summary=article.summary,
            content_markdown=article.content_markdown,
            author_source=article.author_source,
            clinical_verified_by=article.clinical_verified_by,
            reading_time_minutes=calculate_reading_time(article.content_markdown),
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

    @classmethod
    async def get_categories(cls, db: AsyncSession) -> List[HealthCategoryResponse]:
        """Fetch all unique categories with published article counts."""
        query = (
            select(HealthArticle.category, func.count(HealthArticle.id))
            .where(HealthArticle.is_published.is_(True))
            .group_by(HealthArticle.category)
            .order_by(HealthArticle.category.asc())
        )
        res = await db.execute(query)
        rows = res.all()

        return [
            HealthCategoryResponse(name=cat, article_count=count)
            for cat, count in rows
        ]
