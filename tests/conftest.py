"""pytest 公共 fixture。"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

import pytest

from hushai.settings import reset_for_tests


@pytest.fixture(autouse=True)
def _reset_settings(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """避免宿主环境里模式相关变量污染各测试。"""
    monkeypatch.delenv("HUSH_MODE", raising=False)
    monkeypatch.delenv("HUSH_CALM_MODE", raising=False)
    reset_for_tests()
    yield
    reset_for_tests()


# ---------------------------------------------------------------------------
# 冥想模块：内存 SQLite session fixture
#
# 提供一个独立的、建好表的内存 SQLite AsyncSession，供 auth/engine 等需要
# 真实 DB 的单元测试使用。与全局 get_session_factory() 解耦，避免污染。
# ---------------------------------------------------------------------------


@pytest.fixture
async def meditation_session() -> AsyncGenerator:
    """返回一个已建表的内存 SQLite AsyncSession，测试结束自动清理。"""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import StaticPool

    from hushai.meditation.db.models import Base

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def meditation_config(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """注入一个测试用 MeditationConfig（debug=True，无外部依赖），并在结束后还原。

    配置实例通过 ``hushai.meditation.config.get_config()`` 获取；测试结束后
    调用 ``reset_config()`` 清除，避免污染后续测试。
    """
    from hushai.meditation import config as cfg_module

    cfg = cfg_module.MeditationConfig(
        debug=True,
        jwt_secret="test-secret-not-for-prod",
        default_llm_provider="openai",
    )
    cfg_module.set_config(cfg)
    yield
    cfg_module.reset_config()
