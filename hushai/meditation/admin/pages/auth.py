"""登录/登出页面。"""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from hushai.meditation.admin.auth import (
    create_admin_token,
    generate_csrf_token,
    get_admin_from_request,
    set_csrf_cookie,
    verify_admin_credentials_db,
)
from hushai.meditation.admin.pages._shared import templates

router = APIRouter(tags=["admin-web"])


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str | None = None):
    """登录页面。"""
    if get_admin_from_request(request):
        return RedirectResponse(url="/admin/", status_code=302)
    return templates.TemplateResponse(request, "login.html", {"error": error})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """登录处理。设置 admin_token 与 CSRF cookie（生产 HTTPS 启用 secure）。"""
    from hushai.meditation.config import get_config

    admin = await verify_admin_credentials_db(username, password)
    if not admin:
        return templates.TemplateResponse(
            request, "login.html", {"error": "用户名或密码错误"}, status_code=401
        )

    token = create_admin_token(username)
    csrf_token = generate_csrf_token()
    response = RedirectResponse(url="/admin/", status_code=302)
    response.set_cookie(
        "admin_token",
        token,
        httponly=True,
        max_age=86400,
        samesite="lax",
        secure=not get_config().debug,
    )
    set_csrf_cookie(response, csrf_token)
    return response


@router.get("/logout")
async def logout():
    """登出处理。"""
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_token")
    response.delete_cookie("admin_csrf_token")
    return response
