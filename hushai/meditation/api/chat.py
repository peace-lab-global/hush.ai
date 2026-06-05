"""对话 API 路由。"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.app import limiter
from hushai.meditation.core.engine import chat, chat_stream, knowledge_qa
from hushai.meditation.db.models import Conversation, Message, Scene
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    KnowledgeQAResponse,
    SceneListResponse,
    ScenePublicItem,
    StreamChunk,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ConversationItem(BaseModel):
    id: str
    title: str | None
    created_at: Any
    updated_at: Any


class ConversationListResponse(BaseModel):
    conversations: list[ConversationItem]
    total: int


def _extract_token(authorization: str) -> str:
    return extract_bearer_token(authorization)


async def _require_user(
    authorization: str = Header(..., alias="Authorization"),
    session: AsyncSession = Depends(get_session),
) -> str:
    token = _extract_token(authorization)
    try:
        return await get_current_user_id(token, session)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None


@router.post("/", response_model=ChatResponse, responses={401: {"model": ErrorResponse}})
@limiter.limit("30/minute")
async def chat_endpoint(
    request: Request,
    req: ChatRequest,
    user_id: str = Depends(_require_user),
) -> ChatResponse:
    try:
        result = await chat(
            user_id=user_id,
            message=req.message,
            conversation_id=req.conversation_id,
            skill_ids=req.skill_ids,
            provider=req.provider,
            scene_id=req.scene_id,
        )
        return ChatResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.post("/stream", responses={401: {"model": ErrorResponse}})
@limiter.limit("30/minute")
async def chat_stream_endpoint(
    request: Request,
    req: ChatRequest,
    user_id: str = Depends(_require_user),
) -> StreamingResponse:
    async def _generate() -> AsyncGenerator[str, None]:
        try:
            async for chunk in chat_stream(
                user_id=user_id,
                message=req.message,
                conversation_id=req.conversation_id,
                skill_ids=req.skill_ids,
                provider=req.provider,
                scene_id=req.scene_id,
            ):
                data = StreamChunk(**chunk).model_dump_json(exclude_none=True)
                yield f"data: {data}\n\n"
        except RuntimeError as e:
            err = ErrorResponse(error=str(e)).model_dump_json()
            yield f"data: {err}\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")


@router.post(
    "/knowledge",
    response_model=KnowledgeQAResponse,
    responses={401: {"model": ErrorResponse}},
)
@limiter.limit("30/minute")
async def knowledge_qa_endpoint(
    request: Request,
    req: ChatRequest,
    user_id: str = Depends(_require_user),
) -> KnowledgeQAResponse:
    try:
        result = await knowledge_qa(
            user_id=user_id,
            message=req.message,
            conversation_id=req.conversation_id,
            provider=req.provider,
        )
        return KnowledgeQAResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.get("/scenes", response_model=SceneListResponse)
async def list_scenes(
    session: AsyncSession = Depends(get_session),
) -> SceneListResponse:
    """返回所有启用的场景列表（供前台选择）。"""
    result = await session.execute(
        select(Scene)
        .where(Scene.is_active.is_(True))
        .order_by(Scene.sort_order.asc(), Scene.created_at.desc())
    )
    scenes = result.scalars().all()
    return SceneListResponse(
        scenes=[
            ScenePublicItem(
                id=s.id,
                name=s.name,
                slug=s.slug,
                description=s.description,
                opening_message=s.opening_message,
            )
            for s in scenes
        ]
    )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    responses={401: {"model": ErrorResponse}},
)
async def list_conversations(
    user_id: str = Depends(_require_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> ConversationListResponse:
    """返回当前用户的对话列表。"""
    base = select(Conversation).where(
        Conversation.user_id == user_id,
        Conversation.is_active.is_(True),
    )
    count_result = await session.execute(
        select(Conversation.id).where(
            Conversation.user_id == user_id, Conversation.is_active.is_(True)
        )
    )
    total = len(count_result.scalars().all())

    result = await session.execute(
        base.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)
    )
    conversations = [
        ConversationItem(
            id=c.id,
            title=c.title,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in result.scalars().all()
    ]
    return ConversationListResponse(conversations=conversations, total=total)


class MessageItem(BaseModel):
    id: str
    role: str
    content: str
    created_at: Any


class MessageListResponse(BaseModel):
    messages: list[MessageItem]
    conversation_title: str | None


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessageListResponse,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def get_conversation_messages(
    conversation_id: str,
    user_id: str = Depends(_require_user),
    session: AsyncSession = Depends(get_session),
) -> MessageListResponse:
    """返回指定对话的消息历史。"""
    result = await session.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.is_active.is_(True),
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")

    msg_result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = [
        MessageItem(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat(),
        )
        for m in msg_result.scalars().all()
    ]
    return MessageListResponse(
        messages=messages,
        conversation_title=conv.title,
    )
