"""对话 API 路由。"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.core.engine import chat, chat_stream
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    StreamChunk,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


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
async def chat_endpoint(
    req: ChatRequest,
    user_id: str = Depends(_require_user),
) -> ChatResponse:
    try:
        result = await chat(
            user_id=user_id,
            message=req.message,
            conversation_id=req.conversation_id,
        )
        return ChatResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.post("/stream", responses={401: {"model": ErrorResponse}})
async def chat_stream_endpoint(
    req: ChatRequest,
    user_id: str = Depends(_require_user),
) -> StreamingResponse:
    async def _generate() -> AsyncGenerator[str, None]:
        try:
            async for chunk in chat_stream(
                user_id=user_id,
                message=req.message,
                conversation_id=req.conversation_id,
            ):
                data = StreamChunk(**chunk).model_dump_json(exclude_none=True)
                yield f"data: {data}\n\n"
        except RuntimeError as e:
            err = ErrorResponse(error=str(e)).model_dump_json()
            yield f"data: {err}\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")
