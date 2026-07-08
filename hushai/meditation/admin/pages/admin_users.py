"""管理员用户管理页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request, hash_password
from hushai.meditation.admin.pages._shared import login_redirect, templates
from hushai.meditation.db.models import AdminUser
from hushai.meditation.db.session import get_session

router = APIRouter(tags=["admin-web"])


@router.get("/admin-users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """管理员用户管理页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(select(AdminUser).order_by(AdminUser.created_at.desc()))
    admin_users = list(result.scalars().all())

    return templates.TemplateResponse(
        request,
        "admin_users.html",
        {
            "admin_user": admin_user,
            "admin_users": admin_users,
        },
    )


@router.get("/admin-users/new", response_class=HTMLResponse)
async def admin_user_new_page(request: Request):
    """新建管理员表单。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()
    return templates.TemplateResponse(
        request,
        "admin_user_form.html",
        {"admin_user": admin_user, "target": None, "error": None},
    )


@router.post("/admin-users/new")
async def admin_user_create(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    display_name: str = Form(""),
    session: AsyncSession = Depends(get_session),
):
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    username = username.strip()
    password = password.strip()
    display_name_val = display_name.strip() or None

    if not username or len(username) < 2:
        return templates.TemplateResponse(
            request,
            "admin_user_form.html",
            {"admin_user": admin_user, "target": None, "error": "用户名至少2个字符"},
            status_code=400,
        )

    if not password or len(password) < 6:
        return templates.TemplateResponse(
            request,
            "admin_user_form.html",
            {"admin_user": admin_user, "target": None, "error": "密码至少6个字符"},
            status_code=400,
        )

    existing = await session.execute(select(AdminUser).where(AdminUser.username == username))
    if existing.scalar_one_or_none():
        return templates.TemplateResponse(
            request,
            "admin_user_form.html",
            {"admin_user": admin_user, "target": None, "error": f"用户名 '{username}' 已存在"},
            status_code=400,
        )

    admin = AdminUser(
        username=username,
        password_hash=hash_password(password),
        display_name=display_name_val,
    )
    session.add(admin)
    await session.commit()
    return RedirectResponse(url="/admin/admin-users", status_code=302)


@router.get("/admin-users/{admin_id}/edit", response_class=HTMLResponse)
async def admin_user_edit_page(
    request: Request,
    admin_id: str,
    session: AsyncSession = Depends(get_session),
):
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(select(AdminUser).where(AdminUser.id == admin_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="管理员不存在")

    return templates.TemplateResponse(
        request,
        "admin_user_form.html",
        {"admin_user": admin_user, "target": target, "error": None},
    )


@router.post("/admin-users/{admin_id}/edit")
async def admin_user_update(
    request: Request,
    admin_id: str,
    username: str = Form(...),
    password: str = Form(""),
    display_name: str = Form(""),
    is_active: str = Form(""),
    session: AsyncSession = Depends(get_session),
):
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(select(AdminUser).where(AdminUser.id == admin_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="管理员不存在")

    username = username.strip()
    display_name_val = display_name.strip() or None

    if not username or len(username) < 2:
        return templates.TemplateResponse(
            request,
            "admin_user_form.html",
            {"admin_user": admin_user, "target": target, "error": "用户名至少2个字符"},
            status_code=400,
        )

    existing = await session.execute(
        select(AdminUser).where(AdminUser.username == username, AdminUser.id != admin_id)
    )
    if existing.scalar_one_or_none():
        return templates.TemplateResponse(
            request,
            "admin_user_form.html",
            {"admin_user": admin_user, "target": target, "error": f"用户名 '{username}' 已存在"},
            status_code=400,
        )

    target.username = username
    target.display_name = display_name_val
    target.is_active = is_active == "on"

    if password and password.strip():
        if len(password) < 6:
            return templates.TemplateResponse(
                request,
                "admin_user_form.html",
                {"admin_user": admin_user, "target": target, "error": "密码至少6个字符"},
                status_code=400,
            )
        target.password_hash = hash_password(password.strip())

    await session.commit()
    return RedirectResponse(url="/admin/admin-users", status_code=302)


@router.delete("/api/admin-users/{admin_id}")
async def delete_admin_user(
    request: Request,
    admin_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除管理员。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(AdminUser).where(AdminUser.id == admin_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="管理员不存在")

    if target.username == admin_user:
        raise HTTPException(status_code=400, detail="不能删除当前登录的管理员")

    await session.delete(target)
    await session.commit()
    return {"success": True}
