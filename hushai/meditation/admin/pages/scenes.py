"""场景管理页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import get_session, login_redirect, templates
from hushai.meditation.db.models import Scene

router = APIRouter(tags=["admin-web"])


@router.get("/scenes", response_class=HTMLResponse)
async def scenes_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    search: str = "",
    session: AsyncSession = Depends(get_session),
):
    """场景管理列表。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    offset = (page - 1) * limit
    base_query = select(Scene)
    count_query = select(func.count()).select_from(Scene)

    if search:
        like = f"%{search}%"
        base_query = base_query.where(Scene.name.ilike(like) | Scene.description.ilike(like))
        count_query = count_query.where(Scene.name.ilike(like) | Scene.description.ilike(like))

    result = await session.execute(
        base_query.order_by(Scene.sort_order.asc(), Scene.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    scenes = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit if total else 0

    return templates.TemplateResponse(
        request,
        "scenes.html",
        {
            "admin_user": admin_user,
            "scenes": scenes,
            "page": page,
            "total_pages": max(total_pages, 1),
            "total": total,
            "search": search,
            "limit": limit,
        },
    )


@router.get("/scenes/new", response_class=HTMLResponse)
async def scene_new_page(request: Request):
    """新建场景表单。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()
    return templates.TemplateResponse(
        request,
        "scene_form.html",
        {"admin_user": admin_user, "scene": None, "error": None},
    )


@router.post("/scenes/new")
async def scene_create(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    system_prompt: str = Form(...),
    opening_message: str = Form(""),
    sort_order: int = Form(0),
    is_active: str | None = Form(None),
    session: AsyncSession = Depends(get_session),
):
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    name = name.strip()
    slug = slug.strip().lower()
    system_prompt = system_prompt.strip()
    if not name or not slug or not system_prompt:
        return templates.TemplateResponse(
            request,
            "scene_form.html",
            {
                "admin_user": admin_user,
                "scene": None,
                "error": "名称、标识与系统提示不能为空",
            },
            status_code=400,
        )

    # 检查 slug 唯一性
    existing = await session.execute(select(Scene).where(Scene.slug == slug))
    if existing.scalar_one_or_none():
        return templates.TemplateResponse(
            request,
            "scene_form.html",
            {
                "admin_user": admin_user,
                "scene": None,
                "error": f"标识 '{slug}' 已被使用",
            },
            status_code=400,
        )

    scene = Scene(
        name=name[:128],
        slug=slug[:64],
        description=(description.strip()[:512] if description.strip() else None),
        system_prompt=system_prompt,
        opening_message=(opening_message.strip() or None),
        sort_order=sort_order,
        is_active=is_active == "on",
    )
    session.add(scene)
    await session.commit()
    return RedirectResponse(url="/admin/scenes", status_code=302)


@router.get("/scenes/{scene_id}/edit", response_class=HTMLResponse)
async def scene_edit_page(
    request: Request,
    scene_id: str,
    session: AsyncSession = Depends(get_session),
):
    """编辑场景表单。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(select(Scene).where(Scene.id == scene_id))
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="场景不存在")

    return templates.TemplateResponse(
        request,
        "scene_form.html",
        {"admin_user": admin_user, "scene": scene, "error": None},
    )


@router.post("/scenes/{scene_id}/edit")
async def scene_update(
    request: Request,
    scene_id: str,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    system_prompt: str = Form(...),
    opening_message: str = Form(""),
    sort_order: int = Form(0),
    is_active: str = Form(""),
    session: AsyncSession = Depends(get_session),
):
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(select(Scene).where(Scene.id == scene_id))
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="场景不存在")

    name = name.strip()
    slug = slug.strip().lower()
    system_prompt = system_prompt.strip()
    if not name or not slug or not system_prompt:
        return templates.TemplateResponse(
            request,
            "scene_form.html",
            {
                "admin_user": admin_user,
                "scene": scene,
                "error": "名称、标识与系统提示不能为空",
            },
            status_code=400,
        )

    # 检查 slug 唯一性（排除自身）
    existing = await session.execute(select(Scene).where(Scene.slug == slug, Scene.id != scene_id))
    if existing.scalar_one_or_none():
        return templates.TemplateResponse(
            request,
            "scene_form.html",
            {
                "admin_user": admin_user,
                "scene": scene,
                "error": f"标识 '{slug}' 已被使用",
            },
            status_code=400,
        )

    scene.name = name[:128]
    scene.slug = slug[:64]
    scene.description = description.strip()[:512] if description.strip() else None
    scene.system_prompt = system_prompt
    scene.opening_message = opening_message.strip() or None
    scene.sort_order = sort_order
    scene.is_active = is_active == "on"
    await session.commit()
    return RedirectResponse(url="/admin/scenes", status_code=302)


@router.delete("/api/scenes/{scene_id}")
async def delete_scene(
    request: Request,
    scene_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除场景。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(Scene).where(Scene.id == scene_id))
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="场景不存在")

    await session.delete(scene)
    await session.commit()

    return {"success": True}
