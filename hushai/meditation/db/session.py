"""数据库会话管理。"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hushai.meditation.config import get_config

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _resolve_db_url() -> str:
    cfg = get_config()
    url = cfg.postgres_url

    if not url:
        return "sqlite+aiosqlite:///./meditation_local.db"

    if url.startswith("sqlite"):
        if "aiosqlite" not in url:
            url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def get_engine():
    global _engine
    if _engine is None:
        url = _resolve_db_url()
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_async_engine(
            url,
            echo=get_config().debug,
            pool_size=5 if url.startswith("sqlite") else 10,
            connect_args=connect_args,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_db() -> None:
    from hushai.meditation.db.models import Base

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


def reset_session_for_tests() -> None:
    global _engine, _session_factory
    _engine = None
    _session_factory = None
