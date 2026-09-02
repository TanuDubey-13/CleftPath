from datetime import datetime, timezone
import math
from typing import List, Optional
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppException
from app.models.pathguide import PathGuideMessage, PathGuideThread
from app.models.user import User, UserRole
from app.schemas.pathguide import (
    PaginatedPathGuideMessagesResponse,
    PaginatedPathGuideThreadsResponse,
    PathGuideCitation,
    PathGuideMessageCreateRequest,
    PathGuideMessageResponse,
    PathGuideSuggestedPrompt,
    PathGuideSuggestedPromptsResponse,
    PathGuideThreadCreateRequest,
    PathGuideThreadResponse,
    PathGuideThreadUpdateRequest,
)
from app.services.auth_service import AuthService
from app.services.gemini_service import GeminiService
from app.services.rag_service import RAGService


class PathGuideService:
    # ========================================================================
    # Suggested Prompts
    # ========================================================================

    @classmethod
    def get_suggested_prompts(cls) -> PathGuideSuggestedPromptsResponse:
        """Return non-diagnostic educational starter prompts."""
        prompts = [
            PathGuideSuggestedPrompt(
                id="sp_1",
                category="Feeding & Bottles",
                prompt="How do specialized cleft feeders like Dr. Brown's or Pigeon work?",
                description="Understand unidirectional valves and upright feeding positioning.",
            ),
            PathGuideSuggestedPrompt(
                id="sp_2",
                category="Surgical Preparation",
                prompt="What questions are helpful to ask during a pre-op consultation for lip repair?",
                description="Preparation tips and questions for your cleft team.",
            ),
            PathGuideSuggestedPrompt(
                id="sp_3",
                category="Speech Exploration",
                prompt="What are fun, gentle sound imitation games for infants before palate surgery?",
                description="Playful bilabial sound modeling and vocal play ideas.",
            ),
            PathGuideSuggestedPrompt(
                id="sp_4",
                category="Health Library",
                prompt="Can you summarize key recovery care points from the Health Library?",
                description="Educational overview of post-procedure home routines.",
            ),
        ]
        return PathGuideSuggestedPromptsResponse(prompts=prompts)

    # ========================================================================
    # Thread Operations
    # ========================================================================

    @classmethod
    async def list_threads(
        cls,
        db: AsyncSession,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedPathGuideThreadsResponse:
        """List active user's conversation threads ordered by most recent activity."""
        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 50)

        count_res = await db.execute(
            select(func.count(PathGuideThread.id)).where(PathGuideThread.user_id == current_user.id)
        )
        total_items = count_res.scalar() or 0
        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        query = (
            select(PathGuideThread)
            .where(PathGuideThread.user_id == current_user.id)
            .options(selectinload(PathGuideThread.messages))
            .order_by(PathGuideThread.updated_at.desc())
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(query)
        threads = res.scalars().all()

        items = []
        for t in threads:
            msg_count = len(t.messages)
            last_msg = sorted(t.messages, key=lambda m: m.created_at, reverse=True)[0] if t.messages else None
            last_msg_resp = (
                PathGuideMessageResponse(
                    id=last_msg.id,
                    thread_id=last_msg.thread_id,
                    role=last_msg.role,
                    content=last_msg.content,
                    citations=[PathGuideCitation(**c) for c in last_msg.citations] if last_msg.citations else [],
                    safety_flags=last_msg.safety_flags or {},
                    tokens_used=last_msg.tokens_used,
                    created_at=last_msg.created_at,
                )
                if last_msg
                else None
            )

            items.append(
                PathGuideThreadResponse(
                    id=t.id,
                    user_id=t.user_id,
                    patient_id=t.patient_id,
                    title=t.title,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                    message_count=msg_count,
                    last_message=last_msg_resp,
                )
            )

        return PaginatedPathGuideThreadsResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
        )

    @classmethod
    async def get_thread_by_id(
        cls,
        db: AsyncSession,
        thread_id: uuid.UUID,
        current_user: User,
    ) -> PathGuideThreadResponse:
        """Retrieve a single thread with strict IDOR verification."""
        query = (
            select(PathGuideThread)
            .where(PathGuideThread.id == thread_id)
            .options(selectinload(PathGuideThread.messages))
        )
        res = await db.execute(query)
        thread = res.scalar_one_or_none()

        if not thread:
            raise AppException(
                message="Conversation thread not found.",
                code="THREAD_NOT_FOUND",
                status_code=404,
            )

        if thread.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to this conversation thread is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        msg_count = len(thread.messages)
        last_msg = sorted(thread.messages, key=lambda m: m.created_at, reverse=True)[0] if thread.messages else None
        last_msg_resp = (
            PathGuideMessageResponse(
                id=last_msg.id,
                thread_id=last_msg.thread_id,
                role=last_msg.role,
                content=last_msg.content,
                citations=[PathGuideCitation(**c) for c in last_msg.citations] if last_msg.citations else [],
                safety_flags=last_msg.safety_flags or {},
                tokens_used=last_msg.tokens_used,
                created_at=last_msg.created_at,
            )
            if last_msg
            else None
        )

        return PathGuideThreadResponse(
            id=thread.id,
            user_id=thread.user_id,
            patient_id=thread.patient_id,
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            message_count=msg_count,
            last_message=last_msg_resp,
        )

    @classmethod
    async def create_thread(
        cls,
        db: AsyncSession,
        payload: PathGuideThreadCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PathGuideThreadResponse:
        """Create a new conversation thread with optional initial message."""
        title = payload.title.strip() if payload.title and payload.title.strip() else "Care Conversation"
        now = datetime.now(timezone.utc)

        new_thread = PathGuideThread(
            id=uuid.uuid4(),
            user_id=current_user.id,
            patient_id=payload.patient_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        db.add(new_thread)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="PATHGUIDE_THREAD_CREATED",
            resource_type="pathguide_thread",
            resource_id=str(new_thread.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        # If an initial message was provided, process it immediately
        if payload.initial_message and payload.initial_message.strip():
            await cls.create_message(
                db=db,
                thread_id=new_thread.id,
                payload=PathGuideMessageCreateRequest(content=payload.initial_message.strip()),
                current_user=current_user,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return await cls.get_thread_by_id(db, new_thread.id, current_user)

    @classmethod
    async def update_thread(
        cls,
        db: AsyncSession,
        thread_id: uuid.UUID,
        payload: PathGuideThreadUpdateRequest,
        current_user: User,
    ) -> PathGuideThreadResponse:
        """Update thread title with IDOR verification."""
        res = await db.execute(select(PathGuideThread).where(PathGuideThread.id == thread_id))
        thread = res.scalar_one_or_none()

        if not thread:
            raise AppException(
                message="Conversation thread not found.",
                code="THREAD_NOT_FOUND",
                status_code=404,
            )

        if thread.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to update this conversation thread is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        thread.title = payload.title.strip()
        thread.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.commit()

        return await cls.get_thread_by_id(db, thread.id, current_user)

    @classmethod
    async def delete_thread(
        cls,
        db: AsyncSession,
        thread_id: uuid.UUID,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Delete conversation thread and its messages with IDOR verification."""
        res = await db.execute(select(PathGuideThread).where(PathGuideThread.id == thread_id))
        thread = res.scalar_one_or_none()

        if not thread:
            raise AppException(
                message="Conversation thread not found.",
                code="THREAD_NOT_FOUND",
                status_code=404,
            )

        if thread.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to delete this conversation thread is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        await db.delete(thread)
        await db.flush()

        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="PATHGUIDE_THREAD_DELETED",
            resource_type="pathguide_thread",
            resource_id=str(thread_id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

    # ========================================================================
    # Message Operations
    # ========================================================================

    @classmethod
    async def list_messages(
        cls,
        db: AsyncSession,
        thread_id: uuid.UUID,
        current_user: User,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedPathGuideMessagesResponse:
        """List messages in a conversation thread with IDOR verification."""
        # Verify thread ownership
        await cls.get_thread_by_id(db, thread_id, current_user)

        safe_page = max(1, page)
        safe_page_size = min(max(1, page_size), 100)

        count_res = await db.execute(
            select(func.count(PathGuideMessage.id)).where(PathGuideMessage.thread_id == thread_id)
        )
        total_items = count_res.scalar() or 0
        total_pages = max(1, math.ceil(total_items / safe_page_size))
        offset = (safe_page - 1) * safe_page_size

        query = (
            select(PathGuideMessage)
            .where(PathGuideMessage.thread_id == thread_id)
            .order_by(PathGuideMessage.created_at.asc())
            .offset(offset)
            .limit(safe_page_size)
        )
        res = await db.execute(query)
        messages = res.scalars().all()

        items = [
            PathGuideMessageResponse(
                id=m.id,
                thread_id=m.thread_id,
                role=m.role,
                content=m.content,
                citations=[PathGuideCitation(**c) for c in m.citations] if m.citations else [],
                safety_flags=m.safety_flags or {},
                tokens_used=m.tokens_used,
                created_at=m.created_at,
            )
            for m in messages
        ]

        return PaginatedPathGuideMessagesResponse(
            items=items,
            total=total_items,
            page=safe_page,
            page_size=safe_page_size,
            total_pages=total_pages,
            has_next=safe_page < total_pages,
            has_prev=safe_page > 1,
        )

    @classmethod
    async def create_message(
        cls,
        db: AsyncSession,
        thread_id: uuid.UUID,
        payload: PathGuideMessageCreateRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PathGuideMessageResponse:
        """
        Process user message, execute RAG retrieval against published health articles,
        generate grounded AI response, persist conversation records, and log audit event.
        """
        # 1. Verify thread ownership
        thread_res = await db.execute(select(PathGuideThread).where(PathGuideThread.id == thread_id))
        thread = thread_res.scalar_one_or_none()

        if not thread:
            raise AppException(
                message="Conversation thread not found.",
                code="THREAD_NOT_FOUND",
                status_code=404,
            )

        if thread.user_id != current_user.id and current_user.role not in (
            UserRole.ADMIN,
            UserRole.CLINICIAN,
        ):
            raise AppException(
                message="Access to this conversation thread is forbidden.",
                code="FORBIDDEN",
                status_code=403,
            )

        user_content = payload.content.strip()
        if not user_content:
            raise AppException(
                message="Message content cannot be empty.",
                code="INVALID_MESSAGE_CONTENT",
                status_code=400,
            )

        now = datetime.now(timezone.utc)

        # 2. Persist User Message
        user_message = PathGuideMessage(
            id=uuid.uuid4(),
            thread_id=thread.id,
            role="user",
            content=user_content,
            citations=[],
            safety_flags={},
            tokens_used=0,
            created_at=now,
        )
        db.add(user_message)
        await db.flush()

        # 3. RAG Knowledge Retrieval (published health articles only)
        retrieved_items = await RAGService.retrieve_relevant_chunks(db, user_content, limit=4)
        grounded_context, citations = RAGService.format_grounded_context(retrieved_items)

        # 4. Generate AI Grounded Response
        ai_response_text, safety_flags, tokens_used = await GeminiService.generate_response(
            user_query=user_content,
            grounded_context=grounded_context,
            citations=citations,
        )

        # 5. Persist Assistant Message
        citations_json = [c.model_dump() for c in citations]
        assistant_message = PathGuideMessage(
            id=uuid.uuid4(),
            thread_id=thread.id,
            role="assistant",
            content=ai_response_text,
            citations=citations_json,
            safety_flags=safety_flags,
            tokens_used=tokens_used,
            created_at=datetime.now(timezone.utc),
        )
        db.add(assistant_message)

        # Update thread timestamp and title if it's the first message and still default
        thread.updated_at = datetime.now(timezone.utc)
        if thread.title == "Care Conversation":
            # Auto-title from first 40 chars of question
            thread.title = (user_content[:40] + "...") if len(user_content) > 40 else user_content

        await db.flush()

        # 6. Audit Logging
        await AuthService.record_audit_log(
            db=db,
            user_id=current_user.id,
            action="PATHGUIDE_MESSAGE_CREATED",
            resource_type="pathguide_message",
            resource_id=str(assistant_message.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return PathGuideMessageResponse(
            id=assistant_message.id,
            thread_id=assistant_message.thread_id,
            role=assistant_message.role,
            content=assistant_message.content,
            citations=citations,
            safety_flags=assistant_message.safety_flags,
            tokens_used=assistant_message.tokens_used,
            created_at=assistant_message.created_at,
        )
