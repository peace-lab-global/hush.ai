"""知识库管理页面。"""

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
from hushai.meditation.db.models import KnowledgeChunk

router = APIRouter(tags=["admin-web"])


@router.get("/knowledge", response_class=HTMLResponse)
async def knowledge_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    search: str = "",
    session: AsyncSession = Depends(get_session),
):
    """知识库管理页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    offset = (page - 1) * limit

    # 构建查询
    base_query = select(KnowledgeChunk)
    count_query = select(func.count()).select_from(KnowledgeChunk)

    if search:
        base_query = base_query.where(
            (KnowledgeChunk.title.ilike(f"%{search}%"))
            | (KnowledgeChunk.content.ilike(f"%{search}%"))
        )
        count_query = count_query.where(
            (KnowledgeChunk.title.ilike(f"%{search}%"))
            | (KnowledgeChunk.content.ilike(f"%{search}%"))
        )

    # 执行查询
    result = await session.execute(
        base_query.order_by(KnowledgeChunk.created_at.desc()).offset(offset).limit(limit)
    )
    knowledge_items = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit

    return templates.TemplateResponse(
        request,
        "knowledge.html",
        {
            "admin_user": admin_user,
            "knowledge_items": knowledge_items,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "search": search,
            "limit": limit,
        },
    )


@router.get("/knowledge/{item_id}", response_class=HTMLResponse)
async def knowledge_detail_page(
    request: Request,
    item_id: str,
    session: AsyncSession = Depends(get_session),
):
    """知识库详情页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    # 获取知识条目
    result = await session.execute(select(KnowledgeChunk).where(KnowledgeChunk.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")

    return templates.TemplateResponse(
        request,
        "knowledge_detail.html",
        {
            "admin_user": admin_user,
            "item": item,
        },
    )


@router.get("/knowledge-import", response_class=HTMLResponse)
async def knowledge_import_page(
    request: Request,
):
    """知识库导入页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    return templates.TemplateResponse(
        request,
        "knowledge_import.html",
        {
            "admin_user": admin_user,
        },
    )


@router.delete("/api/knowledge/{item_id}")
async def delete_knowledge(
    request: Request,
    item_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除知识条目。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(KnowledgeChunk).where(KnowledgeChunk.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")

    await session.delete(item)
    await session.commit()

    return {"success": True}


@router.post("/api/knowledge/batch-delete")
async def batch_delete_knowledge(
    request: Request,
    req: BatchDeleteRequest,
    session: AsyncSession = Depends(get_session),
):
    """批量删除知识条目。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    if not req.ids:
        return {"deleted": 0}

    result = await session.execute(select(KnowledgeChunk).where(KnowledgeChunk.id.in_(req.ids)))
    items = list(result.scalars().all())
    count = 0
    for item in items:
        await session.delete(item)
        count += 1
    await session.commit()
    return {"deleted": count}
