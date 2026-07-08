"""管理后台页面路由子包。

各资源页面独立成模块，由 ``hushai.meditation.admin`` 聚合挂载。
"""

from __future__ import annotations

from fastapi import APIRouter

from hushai.meditation.admin.pages import (
    admin_users,
    appointments,
    audit,
    auth,
    conversations,
    counseling_dashboard,
    counselors,
    dashboard,
    export,
    knowledge,
    memories,
    orders,
    scenes,
    settings,
    skills,
    users,
)


def build_router() -> APIRouter:
    """聚合所有管理后台页面路由到一个 ``APIRouter``（前缀 /admin）。"""
    router = APIRouter(prefix="/admin", tags=["admin-web"])
    for module in (
        auth,
        dashboard,
        users,
        conversations,
        memories,
        knowledge,
        skills,
        scenes,
        settings,
        admin_users,
        audit,
        export,
        counseling_dashboard,
        counselors,
        appointments,
        orders,
    ):
        router.include_router(module.router)
    return router


__all__ = ["build_router"]
