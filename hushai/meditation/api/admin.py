"""管理员 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.core.memory import get_user_memories
from hushai.meditation.db.models import Conversation, Message, User
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import ErrorResponse, UserProfile

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def _require_admin(
    authorization: str = Header(..., alias="Authorization"),
    session: AsyncSession = Depends(get_session),
) -> str:
    token = extract_bearer_token(authorization)
    try:
        return await get_current_user_id(token, session)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None


@router.get(
    "/users/{user_id}/profile",
    response_model=UserProfile,
    responses={401: {"model": ErrorResponse}},
)
async def get_user_profile(
    user_id: str,
    _admin: str = Depends(_require_admin),
    session: AsyncSession = Depends(get_session),
) -> UserProfile:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    conv_count_stmt = (
        select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
    )
    conv_count = (await session.execute(conv_count_stmt)).scalar() or 0
    msg_count_stmt = (
        select(func.count())
        .select_from(Message)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == user_id)
    )
    msg_count = (await session.execute(msg_count_stmt)).scalar() or 0
    memories, _ = await get_user_memories(session, user_id, limit=100)
    memory_summary: dict[str, int] = {}
    for m in memories:
        memory_summary[m.category] = memory_summary.get(m.category, 0) + 1
    return UserProfile(
        user_id=user.id,
        nickname=user.nickname,
        created_at=user.created_at,
        total_conversations=conv_count,
        total_messages=msg_count,
        memory_summary=memory_summary,
    )


@router.get(
    "/users",
    responses={401: {"model": ErrorResponse}},
)
async def list_users(
    _admin: str = Depends(_require_admin),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict:
    stmt = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    users = list(result.scalars().all())
    count_stmt = select(func.count()).select_from(User)
    total = (await session.execute(count_stmt)).scalar() or 0
    return {
        "users": [
            {
                "id": u.id,
                "nickname": u.nickname,
                "created_at": u.created_at.isoformat(),
                "is_active": u.is_active,
            }
            for u in users
        ],
        "total": total,
    }
