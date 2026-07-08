"""管理后台模块。

原 1667 行的 ``router.py`` 已按资源拆分到 ``pages/`` 子包，由
``pages.build_router()`` 聚合为一个 ``APIRouter``。此处保留 ``router``
导出以兼容 ``app.py`` 的 ``from hushai.meditation.admin import router``。
"""

from __future__ import annotations

from hushai.meditation.admin.pages import build_router

router = build_router()

__all__ = ["router"]
