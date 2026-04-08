"""FastAPI 应用入口。"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hushai.meditation.config import get_config
from hushai.meditation.db.session import close_db, init_db

logger = logging.getLogger("hushai.meditation")

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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
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

    app.include_router(frontend_router)
    app.include_router(login_router)
    app.include_router(chat_router)
    app.include_router(knowledge_router)
    app.include_router(memory_router)
    app.include_router(admin_router)
    app.include_router(admin_web_router)

    # 挂载静态文件
    from fastapi.staticfiles import StaticFiles

    app.mount(
        "/admin/static",
        StaticFiles(directory="hushai/meditation/admin/static"),
        name="admin_static",
    )

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
        "hushai.meditation.app:get_app()",
        host=cfg.host,
        port=cfg.port,
        reload=cfg.debug,
        factory="get_app",
    )
