"""FastAPI 应用入口。"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from hushai.meditation.config import get_config
from hushai.meditation.db.session import close_db, init_db

logger = logging.getLogger("hushai.meditation")

limiter = Limiter(key_func=get_remote_address)
_app: FastAPI | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = get_config()
    logging.basicConfig(
        level=logging.DEBUG if cfg.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("冥想老师服务启动中...")
    await init_db()
    logger.info("数据库初始化完成")

    from hushai.meditation.admin.auth import init_default_admin

    created = await init_default_admin()
    if created:
        logger.info("已创建默认管理员账户，请及时修改密码")

    yield
    await close_db()
    logger.info("冥想老师服务已关闭")


def create_app() -> FastAPI:
    cfg = get_config()
    app = FastAPI(
        title="冥想老师 AI 分身",
        description="具备长期记忆的多租户冥想陪伴服务",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/debug",
        redoc_url="/redoc",
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    cors_origins = cfg.cors_origins if not cfg.debug else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from hushai.meditation.admin import router as admin_web_router
    from hushai.meditation.api.admin import router as admin_router
    from hushai.meditation.api.chat import router as chat_router
    from hushai.meditation.api.frontend import router as frontend_router
    from hushai.meditation.api.knowledge import router as knowledge_router
    from hushai.meditation.api.login import router as login_router
    from hushai.meditation.api.memory import router as memory_router
    from hushai.meditation.api.skills import router as skills_router

    app.include_router(frontend_router)
    app.include_router(login_router)
    app.include_router(chat_router)
    app.include_router(skills_router)
    app.include_router(knowledge_router)
    app.include_router(memory_router)
    app.include_router(admin_router)
    app.include_router(admin_web_router)

    # 挂载静态文件（路径相对本文件，不依赖进程 cwd）
    from fastapi.responses import RedirectResponse
    from fastapi.staticfiles import StaticFiles

    _frontend_static = Path(__file__).resolve().parent / "static"
    _admin_static = Path(__file__).resolve().parent / "admin" / "static"
    app.mount(
        "/static",
        StaticFiles(directory=str(_frontend_static)),
        name="static",
    )
    app.mount(
        "/admin/static",
        StaticFiles(directory=str(_admin_static)),
        name="admin_static",
    )

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return RedirectResponse(url="/static/favicon.svg")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


def get_app() -> FastAPI:
    global _app
    if _app is None:
        _app = create_app()
    return _app


def run() -> None:
    import uvicorn

    cfg = get_config()
    uvicorn.run(
        "hushai.meditation.app:get_app",
        host=cfg.host,
        port=cfg.port,
        reload=cfg.debug,
        factory=True,
    )
