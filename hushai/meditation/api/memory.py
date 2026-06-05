"""客户记忆管理 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.core.memory import get_user_memories
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import ErrorResponse, MemoryItem, MemoryListResponse

router = APIRouter(prefix="/api/memory", tags=["memory"])


async def _require_user(
    authorization: str = Header(..., alias="Authorization"),
    session: AsyncSession = Depends(get_session),
) -> str:
    token = extract_bearer_token(authorization)
    try:
        return await get_current_user_id(token, session)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None


@router.get(
    "/",
    response_model=MemoryListResponse,
    responses={401: {"model": ErrorResponse}},
)
async def list_memories(
    user_id: str = Depends(_require_user),
    category: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> MemoryListResponse:
    memories, total = await get_user_memories(
        session,
        user_id,
        category=category,
        limit=limit,
        offset=offset,
    )
    return MemoryListResponse(
        memories=[
            MemoryItem(
                id=m.id,
                category=m.category,  # type: ignore[arg-type]
                content=m.content,
                summary=m.summary or "",
                importance=m.importance,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in memories
        ],
        total=total,
    )
