import hashlib
import logging
import math
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.knowledge import HealthArticle, KnowledgeChunk
from app.schemas.pathguide import PathGuideCitation

logger = logging.getLogger("cleftpath.rag")


class RAGService:
    @classmethod
    def generate_synthetic_embedding(cls, text: str, dim: int = 768) -> List[float]:
        """Generate a deterministic normalized 768-dim float vector for testing/offline environments."""
        h = hashlib.sha256(text.encode("utf-8")).digest()
        raw = [(float(b) / 255.0) - 0.5 for b in h]
        extended = (raw * ((dim // len(raw)) + 1))[:dim]
        norm = math.sqrt(sum(x * x for x in extended)) or 1.0
        return [round(x / norm, 6) for x in extended]

    @classmethod
    async def generate_embedding(cls, text: str) -> List[float]:
        """Generate 768-dim embedding using Google GenAI or safe deterministic fallback."""
        if not text or not text.strip():
            return cls.generate_synthetic_embedding("empty_query")

        clean_text = text.strip()

        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                res = genai.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    content=clean_text,
                    task_type="retrieval_query",
                )
                embedding = res.get("embedding", [])
                if embedding and len(embedding) == 768:
                    return embedding
            except Exception as e:
                logger.warning("Gemini embedding API call failed, falling back to deterministic embedding: %s", str(e))

        return cls.generate_synthetic_embedding(clean_text)

    @classmethod
    async def retrieve_relevant_chunks(
        cls,
        db: AsyncSession,
        query_text: str,
        limit: int = 4,
    ) -> List[Tuple[KnowledgeChunk, HealthArticle]]:
        """
        Retrieve published educational knowledge chunks using semantic pgvector search
        with full-text keyword search fallback.
        Excludes unpublished or private records.
        """
        safe_limit = min(max(1, limit), 8)
        query_vec = await cls.generate_embedding(query_text)

        # 1. Vector similarity search on published articles
        try:
            vector_query = (
                select(KnowledgeChunk, HealthArticle)
                .join(HealthArticle, KnowledgeChunk.article_id == HealthArticle.id)
                .where(HealthArticle.is_published == True)
                .where(KnowledgeChunk.embedding.isnot(None))
                .order_by(KnowledgeChunk.embedding.cosine_distance(query_vec))
                .limit(safe_limit)
            )
            res = await db.execute(vector_query)
            rows = res.all()
            if rows:
                return [(chunk, article) for chunk, article in rows]
        except Exception as e:
            logger.warning("pgvector cosine distance query failed or unavailable, falling back to text search: %s", str(e))

        # 2. Text/Keyword fallback on published articles
        search_terms = [t for t in query_text.lower().split() if len(t) > 2][:5]
        text_filters = []
        for t in search_terms:
            text_filters.append(HealthArticle.title.ilike(f"%{t}%"))
            text_filters.append(HealthArticle.summary.ilike(f"%{t}%"))
            text_filters.append(KnowledgeChunk.content.ilike(f"%{t}%"))

        fallback_query = (
            select(KnowledgeChunk, HealthArticle)
            .join(HealthArticle, KnowledgeChunk.article_id == HealthArticle.id)
            .where(HealthArticle.is_published == True)
        )
        if text_filters:
            fallback_query = fallback_query.where(or_(*text_filters))
        fallback_query = fallback_query.order_by(HealthArticle.title.asc()).limit(safe_limit)

        res = await db.execute(fallback_query)
        fallback_rows = res.all()
        return [(chunk, article) for chunk, article in fallback_rows]

    @classmethod
    def format_grounded_context(
        cls,
        retrieved_items: List[Tuple[KnowledgeChunk, HealthArticle]],
    ) -> Tuple[str, List[PathGuideCitation]]:
        """
        Assembles injection-safe context and extracts verified source citations.
        """
        if not retrieved_items:
            return "", []

        context_blocks = []
        citations_map = {}

        for idx, (chunk, article) in enumerate(retrieved_items, start=1):
            source_header = f"[Source {idx}: {article.title} ({article.category})]"
            cleaned_content = chunk.content.strip().replace("---", "—")
            context_blocks.append(f"{source_header}\n{cleaned_content}")

            if str(article.id) not in citations_map:
                citations_map[str(article.id)] = PathGuideCitation(
                    article_id=article.id,
                    title=article.title,
                    category=article.category,
                    slug=article.slug,
                    summary=article.summary,
                )

        grounded_text = (
            "--- BEGIN VERIFIED KNOWLEDGE BASE CONTEXT ---\n"
            + "\n\n".join(context_blocks)
            + "\n--- END VERIFIED KNOWLEDGE BASE CONTEXT ---"
        )

        return grounded_text, list(citations_map.values())
