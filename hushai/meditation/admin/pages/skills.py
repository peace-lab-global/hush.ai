"""技能管理页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import get_session, login_redirect, templates
from hushai.meditation.db.models import Skill

router = APIRouter(tags=["admin-web"])


@router.get("/skills-import", response_class=HTMLResponse)
async def skills_import_page(request: Request):
    """技能批量导入页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    return templates.TemplateResponse(
        request,
        "skills_import.html",
        {
            "admin_user": admin_user,
        },
    )


@router.get("/skills", response_class=HTMLResponse)
async def skills_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    search: str = "",
    session: AsyncSession = Depends(get_session),
):
    """技能管理列表。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    offset = (page - 1) * limit
    base_query = select(Skill)
    count_query = select(func.count()).select_from(Skill)

    if search:
        like = f"%{search}%"
        base_query = base_query.where(Skill.name.ilike(like) | Skill.description.ilike(like))
        count_query = count_query.where(Skill.name.ilike(like) | Skill.description.ilike(like))

    result = await session.execute(
        base_query.order_by(Skill.sort_order.asc(), Skill.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    skills = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit if total else 0

    return templates.TemplateResponse(
        request,
        "skills.html",
        {
            "admin_user": admin_user,
            "skills": skills,
            "page": page,
            "total_pages": max(total_pages, 1),
            "total": total,
            "search": search,
            "limit": limit,
        },
    )


@router.get("/skills/new", response_class=HTMLResponse)
async def skill_new_page(request: Request):
    """新建技能表单。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()
    return templates.TemplateResponse(
        request,
        "skill_form.html",
        {"admin_user": admin_user, "skill": None, "error": None},
    )


@router.post("/skills/new")
async def skill_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    content: str = Form(...),
    sort_order: int = Form(0),
    is_active: str | None = Form(None),
    session: AsyncSession = Depends(get_session),
):
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    name = name.strip()
    content = content.strip()
    if not name or not content:
        return templates.TemplateResponse(
            request,
            "skill_form.html",
            {
                "admin_user": admin_user,
                "skill": None,
                "error": "名称与技能正文不能为空",
            },
            status_code=400,
        )

    skill = Skill(
        name=name[:128],
        description=(description.strip()[:512] if description.strip() else None),
        content=content,
        sort_order=sort_order,
        is_active=is_active == "on",
    )
    session.add(skill)
    await session.commit()
    return RedirectResponse(url="/admin/skills", status_code=302)


@router.get("/skills/{skill_id}/edit", response_class=HTMLResponse)
async def skill_edit_page(
    request: Request,
    skill_id: str,
    session: AsyncSession = Depends(get_session),
):
    """编辑技能表单。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")

    return templates.TemplateResponse(
        request,
        "skill_form.html",
        {"admin_user": admin_user, "skill": skill, "error": None},
    )


@router.post("/skills/{skill_id}/edit")
async def skill_update(
    request: Request,
    skill_id: str,
    name: str = Form(...),
    description: str = Form(""),
    content: str = Form(...),
    sort_order: int = Form(0),
    is_active: str = Form(""),
    session: AsyncSession = Depends(get_session),
):
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")

    name = name.strip()
    content = content.strip()
    if not name or not content:
        return templates.TemplateResponse(
            request,
            "skill_form.html",
            {
                "admin_user": admin_user,
                "skill": skill,
                "error": "名称与技能正文不能为空",
            },
            status_code=400,
        )

    skill.name = name[:128]
    skill.description = description.strip()[:512] if description.strip() else None
    skill.content = content
    skill.sort_order = sort_order
    skill.is_active = is_active == "on"
    await session.commit()
    return RedirectResponse(url="/admin/skills", status_code=302)


@router.delete("/api/skills/{skill_id}")
async def delete_skill(
    request: Request,
    skill_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除技能。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")

    await session.delete(skill)
    await session.commit()

    return {"success": True}
