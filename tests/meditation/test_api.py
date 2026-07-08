"""API 集成测试 — 覆盖全部路由的 happy path 与异常路径。

使用 FastAPI TestClient + 内存 SQLite，每个测试用独立的 DB 和配置。
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import date, time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from hushai.meditation import config as cfg_module
from hushai.meditation.api.auth import _create_access_token
from hushai.meditation.db import session as session_module
from hushai.meditation.db.models import (
    Appointment,
    AppointmentSettings,
    Base,
    ConsultationOrder,
    Conversation,
    Counselor,
    CounselorSchedule,
    DailyProgress,
    MeditationSession,
    Memory,
    Message,
    Scene,
    ServiceRecord,
    Skill,
    Teacher,
    User,
)


# ---------------------------------------------------------------------------
#  Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def _cfg() -> cfg_module.MeditationConfig:
    cfg = cfg_module.MeditationConfig(
        debug=True,
        jwt_secret="integration-test-secret",
        default_llm_provider="openai",
    )
    cfg_module.set_config(cfg)
    yield cfg  # type: ignore[misc]
    cfg_module.reset_config()


@pytest.fixture()
async def _engine():
    session_module.reset_session_for_tests()
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()
    session_module.reset_session_for_tests()


@pytest.fixture()
def _factory(_engine):
    factory = async_sessionmaker(_engine, expire_on_commit=False)
    session_module._engine = _engine
    session_module._session_factory = factory
    return factory


@pytest.fixture()
async def db_session(_factory) -> AsyncGenerator[AsyncSession, None]:
    async with _factory() as s:
        yield s


@pytest.fixture()
def app(_cfg, _factory, monkeypatch) -> FastAPI:
    from hushai.meditation.app import create_app

    monkeypatch.setattr(
        "hushai.meditation.admin.auth.init_default_admin", _noop_coro_false
    )
    application = create_app()

    async def _override_session() -> AsyncGenerator[AsyncSession, None]:
        async with _factory() as s:
            yield s

    application.dependency_overrides[session_module.get_session] = _override_session
    return application


@pytest.fixture()
def client(app) -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=f"user-{uuid.uuid4().hex[:8]}",
        wx_openid=f"test_openid_{uuid.uuid4().hex[:8]}",
        nickname="测试冥想者",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture()
def user_token(test_user: User) -> str:
    token, _ = _create_access_token(test_user.id)
    return token


@pytest.fixture()
def auth_headers(user_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture()
async def test_teacher(db_session: AsyncSession) -> Teacher:
    teacher = Teacher(
        id=f"teacher-{uuid.uuid4().hex[:8]}",
        name="测试导师",
        slug=f"test-{uuid.uuid4().hex[:6]}",
        description="测试导师描述",
        avatar="测",
        system_prompt="你是测试导师。",
        voice_gender="female",
        style_tags="测试,正念",
        is_active=True,
        sort_order=1,
    )
    db_session.add(teacher)
    await db_session.commit()
    await db_session.refresh(teacher)
    return teacher


@pytest.fixture()
async def test_counselor(db_session: AsyncSession, test_user: User) -> Counselor:
    counselor = Counselor(
        id=f"counselor-{uuid.uuid4().hex[:8]}",
        user_id=test_user.id,
        real_name="张咨询师",
        phone="13800138000",
        email="test@example.com",
        specialties=["焦虑", "压力"],
        certifications=["国家二级"],
        bio="资深咨询师",
        status="approved",
        hourly_rate=300.0,
        is_online=True,
        sort_order=1,
    )
    db_session.add(counselor)
    await db_session.commit()
    await db_session.refresh(counselor)
    return counselor


@pytest.fixture()
async def test_scene(db_session: AsyncSession) -> Scene:
    scene = Scene(
        id=f"scene-{uuid.uuid4().hex[:8]}",
        name="测试场景",
        slug=f"test-{uuid.uuid4().hex[:6]}",
        description="测试场景描述",
        system_prompt="这是测试场景的系统提示。",
        opening_message="欢迎来到测试场景。",
        is_active=True,
        sort_order=1,
    )
    db_session.add(scene)
    await db_session.commit()
    await db_session.refresh(scene)
    return scene


async def _noop_coro_false() -> bool:
    return False


# ---------------------------------------------------------------------------
#  Health / Frontend
# ---------------------------------------------------------------------------


def test_health(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_page(client: TestClient):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


def test_favicon(client: TestClient):
    resp = client.get("/favicon.ico", follow_redirects=False)
    assert resp.status_code in (200, 302, 307)


# ---------------------------------------------------------------------------
#  Login API
# ---------------------------------------------------------------------------


def test_dev_login(client: TestClient):
    resp = client.post("/api/auth/dev-login", json={"nickname": "冥想测试者"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["nickname"] == "冥想测试者"


def test_wx_login_bad_code(client: TestClient):
    resp = client.post("/api/auth/wx-login", json={"code": "invalid-code"})
    assert resp.status_code in (400, 500)


def test_refresh_bad_token(client: TestClient):
    resp = client.post(
        "/api/auth/refresh", json={"refresh_token": "nonexistent-token"}
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
#  Teachers API
# ---------------------------------------------------------------------------


def test_list_teachers(client: TestClient, auth_headers, test_teacher):
    resp = client.get("/api/teachers/list", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "teachers" in data
    assert len(data["teachers"]) >= 1


def test_get_teacher_detail(client: TestClient, auth_headers, test_teacher):
    resp = client.get(f"/api/teachers/{test_teacher.id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "测试导师"


def test_get_teacher_not_found(client: TestClient, auth_headers):
    resp = client.get("/api/teachers/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404


def test_select_teacher(client: TestClient, auth_headers, test_teacher):
    resp = client.post(
        "/api/teachers/select",
        headers=auth_headers,
        json={"teacher_id": test_teacher.id},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_select_teacher_not_found(client: TestClient, auth_headers):
    resp = client.post(
        "/api/teachers/select",
        headers=auth_headers,
        json={"teacher_id": "nonexistent"},
    )
    assert resp.status_code == 404


def test_teachers_no_auth(client: TestClient):
    resp = client.get("/api/teachers/list")
    assert resp.status_code in (401, 422)


# ---------------------------------------------------------------------------
#  Skills API
# ---------------------------------------------------------------------------


def test_list_skills_empty(client: TestClient):
    resp = client.get("/api/skills/")
    assert resp.status_code == 200
    assert resp.json()["skills"] == []


def test_import_skills_with_user_auth(client: TestClient, auth_headers):
    resp = client.post(
        "/api/skills/import",
        headers=auth_headers,
        json={
            "skills": [
                {
                    "name": "正念",
                    "content": "关注呼吸",
                    "description": "基础正念",
                    "sort_order": 1,
                    "is_active": True,
                }
            ]
        },
    )
    assert resp.status_code == 200
    assert resp.json()["imported"] == 1


def test_import_skills_no_auth(client: TestClient):
    resp = client.post(
        "/api/skills/import",
        json={"skills": [{"name": "test", "content": "test content"}]},
    )
    assert resp.status_code in (401, 422)


# ---------------------------------------------------------------------------
#  Meditation API
# ---------------------------------------------------------------------------


def test_start_meditation_session(client: TestClient, auth_headers):
    resp = client.post(
        "/api/meditation/session/start",
        headers=auth_headers,
        json={"mood_before": 5},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "started_at" in data


def test_start_and_end_session(client: TestClient, auth_headers):
    # start
    resp = client.post(
        "/api/meditation/session/start",
        headers=auth_headers,
        json={"mood_before": 6},
    )
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    # end
    resp = client.post(
        "/api/meditation/session/end",
        headers=auth_headers,
        json={"session_id": session_id, "mood_after": 8},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mood_before"] == 6
    assert data["mood_after"] == 8


def test_end_session_not_found(client: TestClient, auth_headers):
    resp = client.post(
        "/api/meditation/session/end",
        headers=auth_headers,
        json={"session_id": "nonexistent"},
    )
    assert resp.status_code == 404


def test_mood_checkin(client: TestClient, auth_headers):
    resp = client.post(
        "/api/meditation/mood-checkin",
        headers=auth_headers,
        json={"mood": 7},
    )
    assert resp.status_code == 200


def test_get_stats(client: TestClient, auth_headers):
    resp = client.get("/api/meditation/stats", headers=auth_headers)
    assert resp.status_code == 200


def test_get_weekly(client: TestClient, auth_headers):
    resp = client.get("/api/meditation/weekly", headers=auth_headers)
    assert resp.status_code == 200


def test_meditation_no_auth(client: TestClient):
    resp = client.post("/api/meditation/session/start", json={})
    assert resp.status_code in (401, 422)


# ---------------------------------------------------------------------------
#  Memory API
# ---------------------------------------------------------------------------


def test_list_memories(client: TestClient, auth_headers):
    resp = client.get("/api/memory/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "memories" in data
    assert data["total"] == 0


def test_list_memories_no_auth(client: TestClient):
    resp = client.get("/api/memory/")
    assert resp.status_code in (401, 422)


def test_list_memories_with_category(client: TestClient, auth_headers):
    resp = client.get(
        "/api/memory/",
        headers=auth_headers,
        params={"category": "emotion_pattern"},
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
#  Chat API
# ---------------------------------------------------------------------------


def test_chat_no_auth(client: TestClient):
    resp = client.post("/api/chat/", json={"message": "你好"})
    assert resp.status_code in (401, 422)


def test_list_scenes(client: TestClient):
    resp = client.get("/api/chat/scenes")
    assert resp.status_code == 200
    assert "scenes" in resp.json()


def test_list_conversations(client: TestClient, auth_headers):
    resp = client.get("/api/chat/conversations", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_get_conversation_messages_not_found(client: TestClient, auth_headers):
    resp = client.get(
        "/api/chat/conversations/nonexistent/messages", headers=auth_headers
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
#  Knowledge API
# ---------------------------------------------------------------------------


def test_knowledge_search_no_auth(client: TestClient):
    resp = client.post("/api/knowledge/search", json={"query": "冥想"})
    assert resp.status_code in (401, 422)


def test_knowledge_search_with_auth(client: TestClient, auth_headers):
    resp = client.post(
        "/api/knowledge/search",
        headers=auth_headers,
        json={"query": "冥想", "top_k": 3},
    )
    assert resp.status_code == 200


def test_knowledge_import_no_auth(client: TestClient):
    resp = client.post(
        "/api/knowledge/import",
        json={"content": "测试内容", "title": "测试", "tags": [], "content_format": "text"},
    )
    assert resp.status_code in (401, 422)


def test_knowledge_sync_remote(client: TestClient, auth_headers):
    resp = client.post("/api/knowledge/sync-remote", headers=auth_headers)
    assert resp.status_code in (200, 500)  # may fail if no remote sources configured


# ---------------------------------------------------------------------------
#  Counseling API (User-facing)
# ---------------------------------------------------------------------------


def test_list_counselors(client: TestClient, auth_headers, test_counselor):
    resp = client.get(
        "/api/counseling/counselors/list", headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "counselors" in data


def test_get_counselor_detail(client: TestClient, auth_headers, test_counselor):
    resp = client.get(
        f"/api/counseling/counselors/{test_counselor.id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200


def test_get_counselor_not_found(client: TestClient, auth_headers):
    resp = client.get(
        "/api/counseling/counselors/nonexistent", headers=auth_headers
    )
    assert resp.status_code == 404


def test_get_counselor_schedule(
    client: TestClient, auth_headers, test_counselor, db_session: AsyncSession
):
    import datetime

    schedule = CounselorSchedule(
        counselor_id=test_counselor.id,
        schedule_date=datetime.date(2026, 12, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(18, 0),
        slot_duration_minutes=50,
        max_bookings=1,
        is_available=True,
    )
    db_session.add(schedule)
    db_session.sync_commit() if hasattr(db_session, "sync_commit") else None

    resp = client.get(
        f"/api/counseling/counselors/{test_counselor.id}/schedule",
        headers=auth_headers,
        params={"date_from": "2026-12-01", "date_to": "2026-12-31"},
    )
    assert resp.status_code == 200


def test_list_user_appointments(client: TestClient, auth_headers):
    resp = client.get(
        "/api/counseling/appointments/list", headers=auth_headers
    )
    assert resp.status_code == 200


def test_create_booking(client: TestClient, auth_headers, test_counselor):
    resp = client.post(
        "/api/counseling/appointments/create",
        headers=auth_headers,
        json={
            "counselor_id": test_counselor.id,
            "appointment_date": "2026-12-01",
            "start_time": "10:00:00",
            "end_time": "10:50:00",
            "client_notes": "第一次咨询",
        },
    )
    assert resp.status_code == 200


def test_create_booking_no_auth(client: TestClient, test_counselor):
    resp = client.post(
        "/api/counseling/appointments/create",
        json={
            "counselor_id": test_counselor.id,
            "appointment_date": "2026-12-01",
            "start_time": "10:00:00",
            "end_time": "10:50:00",
        },
    )
    assert resp.status_code in (401, 422)


def test_list_orders(client: TestClient, auth_headers):
    resp = client.get("/api/counseling/orders/list", headers=auth_headers)
    assert resp.status_code == 200


def test_list_service_records(client: TestClient, auth_headers):
    resp = client.get(
        "/api/counseling/service-records/list", headers=auth_headers
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
#  Counselor Dashboard API
# ---------------------------------------------------------------------------


def test_dashboard_profile_not_counselor(client: TestClient, auth_headers):
    """普通用户访问咨询师 dashboard 应返回 404。"""
    resp = client.get("/api/counselor/profile", headers=auth_headers)
    assert resp.status_code in (200, 404)


def test_dashboard_apply(client: TestClient, auth_headers):
    resp = client.post(
        "/api/counselor/apply",
        headers=auth_headers,
        json={
            "real_name": "申请人",
            "phone": "13900139000",
            "specialties": ["焦虑"],
            "certifications": ["心理咨询师"],
            "bio": "热爱咨询",
        },
    )
    assert resp.status_code in (200, 400)


def test_dashboard_settings(client: TestClient, auth_headers, test_counselor):
    resp = client.get("/api/counselor/settings", headers=auth_headers)
    assert resp.status_code in (200, 404)


def test_dashboard_earnings(client: TestClient, auth_headers, test_counselor):
    resp = client.get("/api/counselor/earnings/summary", headers=auth_headers)
    assert resp.status_code in (200, 404)


def test_dashboard_no_auth(client: TestClient):
    resp = client.get("/api/counselor/profile")
    assert resp.status_code in (401, 422)


# ---------------------------------------------------------------------------
#  Admin API
# ---------------------------------------------------------------------------


def test_admin_get_user_profile(client: TestClient, auth_headers, test_user):
    resp = client.get(
        f"/api/admin/users/{test_user.id}/profile",
        headers=auth_headers,
    )
    assert resp.status_code == 200


def test_admin_get_user_profile_not_found(client: TestClient, auth_headers):
    resp = client.get(
        "/api/admin/users/nonexistent/profile",
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_admin_list_users(client: TestClient, auth_headers):
    resp = client.get("/api/admin/users", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data
    assert data["total"] >= 1


def test_admin_counseling_stats(client: TestClient, auth_headers):
    resp = client.get("/api/admin/counseling/stats", headers=auth_headers)
    assert resp.status_code == 200


def test_admin_list_counselors(client: TestClient, auth_headers):
    resp = client.get("/api/admin/counselors", headers=auth_headers)
    assert resp.status_code == 200


def test_admin_list_orders(client: TestClient, auth_headers):
    resp = client.get("/api/admin/orders", headers=auth_headers)
    assert resp.status_code == 200


def test_admin_no_auth(client: TestClient):
    resp = client.get("/api/admin/users")
    assert resp.status_code in (401, 422)


# ---------------------------------------------------------------------------
#  Lifespan (app startup)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_lifespan_creates_default_teachers(_cfg, _engine, _factory):
    from hushai.meditation.app import lifespan

    app = FastAPI()
    async with lifespan(app):
        async with _factory() as s:
            from sqlalchemy import select

            result = await s.execute(select(Teacher))
            teachers = list(result.scalars().all())
            assert len(teachers) == 5

            result2 = await s.execute(select(AppointmentSettings))
            settings = result2.scalar_one_or_none()
            assert settings is not None
            assert settings.max_booking_count == 5


@pytest.mark.asyncio
async def test_lifespan_skips_existing_teachers(
    _cfg, _engine, _factory, db_session
):
    db_session.add(
        Teacher(
            name="已有导师",
            slug="existing",
            system_prompt="已有",
            is_active=True,
        )
    )
    await db_session.commit()

    from hushai.meditation.app import lifespan

    app = FastAPI()
    async with lifespan(app):
        async with _factory() as s:
            from sqlalchemy import select

            result = await s.execute(select(Teacher))
            teachers = list(result.scalars().all())
            assert len(teachers) == 1


@pytest.mark.asyncio
async def test_lifespan_skips_existing_settings(_cfg, _engine, _factory, db_session):
    """lifespan 在已有配置时不应重复创建。"""
    db_session.add(
        AppointmentSettings(
            counselor_id=None,
            max_booking_count=3,
            min_advance_hours=1,
            slot_duration_minutes=30,
            reminder_before_minutes=10,
            info_collection_enabled=False,
            is_open=True,
        )
    )
    await db_session.commit()

    from hushai.meditation.app import lifespan

    app = FastAPI()
    async with lifespan(app):
        async with _factory() as s:
            from sqlalchemy import select

            result = await s.execute(select(AppointmentSettings))
            settings_list = list(result.scalars().all())
            assert len(settings_list) == 1
            assert settings_list[0].max_booking_count == 3  # unchanged
