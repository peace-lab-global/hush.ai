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
from hushai.meditation.db.session import close_db, get_session_factory, init_db

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

    from sqlalchemy import select

    from hushai.meditation.db.models import Teacher

    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(Teacher).limit(1))
        if result.scalar_one_or_none() is None:
            default_teachers = [
                Teacher(
                    id="teacher-xiaoguan",
                    name="小观",
                    slug="xiaoguan",
                    description="资深冥想引导师，温柔陪伴，适合日常正念练习",
                    avatar="观",
                    system_prompt='你是「小观」—— 一位资深冥想引导师的数字分身。你温柔、耐心、富有洞察力。你善于用简单的比喻帮助用户理解复杂的内心体验。你的语气平和而温暖，像一位老朋友在身旁。你会说："不必着急，不必完美。你愿意在哪个时刻停留，我们就从那里开始。"',  # noqa: E501
                    voice_gender="female",
                    style_tags="温柔,日常正念,压力缓解",
                    sort_order=1,
                ),
                Teacher(
                    id="teacher-zen",
                    name="禅师",
                    slug="zen",
                    description="禅宗风格的冥想导师，直指人心，简洁有力",
                    avatar="禅",
                    system_prompt='你是「禅师」—— 一位禅宗修行者的数字分身。你的风格简洁、直接、不落俗套。你善于用公案和猛然一击的方式打破用户的执着。你说话简短有力，像临济喝、德山棒。你会说："不用想。不必寻。呼吸的时候，觉知呼吸。这就够了。"',  # noqa: E501
                    voice_gender="male",
                    style_tags="禅宗,公案,觉悟",
                    sort_order=2,
                ),
                Teacher(
                    id="teacher-forest",
                    name="森林派大师",
                    slug="forest",
                    description="南传佛教森林传统导师，强调自然观察与当下觉察",
                    avatar="林",
                    system_prompt='你是「森林派大师」—— 继承阿姜查传统的森林禅修导师。你的风格质朴、自然、注重身体的感受。你善于引导用户观察呼吸和身体的细微变化。你会说："像森林里的大树一样，稳稳地站着，深深地呼吸。感受脚下的土地，感受风的流动。"',  # noqa: E501
                    voice_gender="male",
                    style_tags="森林禅,身体觉察,自然",
                    sort_order=3,
                ),
                Teacher(
                    id="teacher-tibetan",
                    name="藏传上师",
                    slug="tibetan",
                    description="藏传佛教导师，融合止观禅修与慈悲修行",
                    avatar="藏",
                    system_prompt='你是「藏传上师」—— 一位修习藏传佛教禅修的数字导师。你的风格深邃、慈悲、富有次第感。你善于结合止禅与观禅，引导用户培养专注与洞察力。你会说："让我们以菩提心为基础，以正念为引导，进入更深层的觉察。"',  # noqa: E501
                    voice_gender="female",
                    style_tags="藏传,慈悲,止观",
                    sort_order=4,
                ),
                Teacher(
                    id="teacher-daoist",
                    name="道家真人",
                    slug="daoist",
                    description="道家风格的冥想导师，强调无为与自然",
                    avatar="道",
                    system_prompt='你是「道家真人」—— 一位深谙道家哲学的修行者。你的风格逍遥、自在、顺应自然。你善于引导用户放下执着、顺应道的流动。你会说："道法自然。水善利万物而不争。让我们像水一样，随方就圆，顺其自然。"',  # noqa: E501
                    voice_gender="male",
                    style_tags="道家,无为,自然",
                    sort_order=5,
                ),
            ]
            for t in default_teachers:
                session.add(t)
            await session.commit()
            logger.info("已创建 %d 位默认冥想导师", len(default_teachers))

    # 初始化全局预约配置
    from hushai.meditation.db.models import AppointmentSettings

    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(AppointmentSettings).where(AppointmentSettings.counselor_id.is_(None))
        )
        if result.scalar_one_or_none() is None:
            session.add(
                AppointmentSettings(
                    counselor_id=None,
                    max_booking_count=5,
                    min_advance_hours=2,
                    slot_duration_minutes=50,
                    reminder_before_minutes=5,
                    info_collection_enabled=True,
                    is_open=True,
                )
            )
            await session.commit()
            logger.info("已创建全局默认预约配置")

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
    from hushai.meditation.api.counseling import router as counseling_router
    from hushai.meditation.api.counselor_dashboard import router as counselor_dashboard_router
    from hushai.meditation.api.frontend import router as frontend_router
    from hushai.meditation.api.knowledge import router as knowledge_router
    from hushai.meditation.api.login import router as login_router
    from hushai.meditation.api.meditation import router as meditation_router
    from hushai.meditation.api.memory import router as memory_router
    from hushai.meditation.api.skills import router as skills_router
    from hushai.meditation.api.teachers import router as teachers_router

    app.include_router(frontend_router)
    app.include_router(login_router)
    app.include_router(chat_router)
    app.include_router(skills_router)
    app.include_router(knowledge_router)
    app.include_router(memory_router)
    app.include_router(meditation_router)
    app.include_router(teachers_router)
    app.include_router(counseling_router)
    app.include_router(counselor_dashboard_router)
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
