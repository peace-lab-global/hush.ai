"""记忆管理页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import (
    BatchDeleteRequest,
    get_session,
    login_redirect,
    templates,
)
from hushai.meditation.db.models import Memory, User

router = APIRouter(tags=["admin-web"])


@router.get("/memories", response_class=HTMLResponse)
async def memories_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    user_id: str | None = None,
    category: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """记忆管理页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    offset = (page - 1) * limit

    # 构建查询
    base_query = select(Memory, User.nickname).join(User, Memory.user_id == User.id)
    count_query = select(func.count()).select_from(Memory)

    if user_id:
        base_query = base_query.where(Memory.user_id == user_id)
        count_query = count_query.where(Memory.user_id == user_id)

    if category:
        base_query = base_query.where(Memory.category == category)
        count_query = count_query.where(Memory.category == category)

    # 执行查询
    result = await session.execute(
        base_query.order_by(Memory.created_at.desc()).offset(offset).limit(limit)
    )
    memories = [{"memory": row[0], "nickname": row[1]} for row in result.all()]
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit

    # 获取用户列表
    users_result = await session.execute(select(User).order_by(User.created_at.desc()).limit(100))
    users = list(users_result.scalars().all())

    # 获取分类列表
    category_result = await session.execute(
        select(Memory.category).distinct().order_by(Memory.category)
    )
    categories = [row[0] for row in category_result.all()]

    return templates.TemplateResponse(
        request,
        "memories.html",
        {
            "admin_user": admin_user,
            "memories": memories,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "user_id": user_id,
            "category": category,
            "users": users,
            "categories": categories,
            "limit": limit,
        },
    )


@router.delete("/api/memories/{memory_id}")
async def delete_memory(
    request: Request,
    memory_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除记忆。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="记忆不存在")

    await session.delete(memory)
    await session.commit()

    return {"success": True}


@router.post("/api/memories/batch-delete")
async def batch_delete_memories(
    request: Request,
    req: BatchDeleteRequest,
    session: AsyncSession = Depends(get_session),
):
    """批量删除记忆。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    if not req.ids:
        return {"deleted": 0}

    result = await session.execute(select(Memory).where(Memory.id.in_(req.ids)))
    memories = list(result.scalars().all())
    count = 0
    for mem in memories:
        await session.delete(mem)
        count += 1
    await session.commit()
    return {"deleted": count}
