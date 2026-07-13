"""补充核心模块单元测试 — encryption、scenes、skills、session、memory。"""

from __future__ import annotations

import pytest

from hushai.meditation import config as cfg_module

# ---------------------------------------------------------------------------
#  encryption
# ---------------------------------------------------------------------------


class TestEncryption:
    @pytest.fixture(autouse=True)
    def _reset(self, monkeypatch):
        monkeypatch.delenv("MEDITATION_ENCRYPTION_KEY", raising=False)
        from hushai.meditation.core import encryption

        encryption.reset_encryption()
        yield
        encryption.reset_encryption()

    def test_encrypt_decrypt_roundtrip(self):
        from hushai.meditation.core.encryption import decrypt_field, encrypt_field

        plain = "这是敏感信息"
        cipher = encrypt_field(plain)
        assert cipher != plain
        assert decrypt_field(cipher) == plain

    def test_encrypt_none_returns_none(self):
        from hushai.meditation.core.encryption import encrypt_field

        assert encrypt_field(None) is None
        assert encrypt_field("") == ""

    def test_decrypt_none_returns_none(self):
        from hushai.meditation.core.encryption import decrypt_field

        assert decrypt_field(None) is None
        assert decrypt_field("") == ""

    def test_decrypt_invalid_returns_original(self):
        from hushai.meditation.core.encryption import decrypt_field

        assert decrypt_field("not-a-valid-cipher") == "not-a-valid-cipher"

    def test_mask_phone(self):
        from hushai.meditation.core.encryption import mask_phone

        assert mask_phone("13812345678") == "138****5678"
        assert mask_phone("123") == "123"  # too short
        assert mask_phone(None) is None
        assert mask_phone("") == ""

    def test_mask_id_number(self):
        from hushai.meditation.core.encryption import mask_id_number

        assert mask_id_number("110101199001011234") == "110***********1234"
        assert mask_id_number("12345") == "12345"  # too short
        assert mask_id_number(None) is None

    def test_mask_name(self):
        from hushai.meditation.core.encryption import mask_name

        assert mask_name("张三") == "张*"
        assert mask_name("张") == "张"
        assert mask_name("欧阳修文") == "欧**文"
        assert mask_name(None) is None
        assert mask_name("") == ""

    def test_auto_generate_key(self, monkeypatch):
        monkeypatch.delenv("MEDITATION_ENCRYPTION_KEY", raising=False)
        from hushai.meditation.core.encryption import (
            _get_fernet,
            reset_encryption,
        )

        reset_encryption()
        f = _get_fernet()
        assert f is not None
        # second call returns same instance
        assert _get_fernet() is f


# ---------------------------------------------------------------------------
#  scenes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_scene_context_empty_id(meditation_session):
    from hushai.meditation.core.scenes import get_scene_context_for_prompt

    result = await get_scene_context_for_prompt(meditation_session, None)
    assert result == ""

    result2 = await get_scene_context_for_prompt(meditation_session, "")
    assert result2 == ""


@pytest.mark.asyncio
async def test_get_scene_context_not_found(meditation_session):
    from hushai.meditation.core.scenes import get_scene_context_for_prompt

    result = await get_scene_context_for_prompt(meditation_session, "nonexistent")
    assert result == ""


@pytest.mark.asyncio
async def test_get_scene_context_found(meditation_session):
    from hushai.meditation.core.scenes import get_scene_context_for_prompt
    from hushai.meditation.db.models import Scene

    scene = Scene(
        name="测试场景",
        slug="test-scene-ctx",
        system_prompt="这是系统提示",
        opening_message="欢迎",
        is_active=True,
    )
    meditation_session.add(scene)
    await meditation_session.commit()
    await meditation_session.refresh(scene)

    result = await get_scene_context_for_prompt(meditation_session, scene.id)
    assert "这是系统提示" in result
    assert "欢迎" in result


@pytest.mark.asyncio
async def test_get_scene_context_inactive(meditation_session):
    from hushai.meditation.core.scenes import get_scene_context_for_prompt
    from hushai.meditation.db.models import Scene

    scene = Scene(
        name="禁用场景",
        slug="inactive-scene",
        system_prompt="不应出现",
        is_active=False,
    )
    meditation_session.add(scene)
    await meditation_session.commit()
    await meditation_session.refresh(scene)

    result = await get_scene_context_for_prompt(meditation_session, scene.id)
    assert result == ""


# ---------------------------------------------------------------------------
#  skills
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_skills_context_none_ids(meditation_session):
    from hushai.meditation.core.skills import get_skills_context_for_prompt

    result = await get_skills_context_for_prompt(meditation_session, None)
    # None means auto-mount: should query active skills
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_get_skills_context_empty_list(meditation_session):
    from hushai.meditation.core.skills import get_skills_context_for_prompt

    result = await get_skills_context_for_prompt(meditation_session, [])
    assert result == ""


@pytest.mark.asyncio
async def test_get_skills_context_with_skills(meditation_session):
    from hushai.meditation.core.skills import get_skills_context_for_prompt
    from hushai.meditation.db.models import Skill

    skill = Skill(
        name="正念呼吸",
        content="关注呼吸的进出",
        is_active=True,
        sort_order=1,
    )
    meditation_session.add(skill)
    await meditation_session.commit()
    await meditation_session.refresh(skill)

    result = await get_skills_context_for_prompt(meditation_session, [skill.id])
    assert "关注呼吸" in result


# ---------------------------------------------------------------------------
#  session module
# ---------------------------------------------------------------------------


def test_resolve_db_url_default():
    from hushai.meditation.db.session import _resolve_db_url, reset_session_for_tests

    reset_session_for_tests()
    cfg_module.set_config(cfg_module.MeditationConfig(postgres_url=""))
    url = _resolve_db_url()
    assert "sqlite" in url
    cfg_module.reset_config()


def test_resolve_db_url_sqlite():
    from hushai.meditation.db.session import _resolve_db_url, reset_session_for_tests

    reset_session_for_tests()
    cfg_module.set_config(cfg_module.MeditationConfig(postgres_url="sqlite:///test.db"))
    url = _resolve_db_url()
    assert "aiosqlite" in url
    cfg_module.reset_config()


def test_resolve_db_url_postgres():
    from hushai.meditation.db.session import _resolve_db_url, reset_session_for_tests

    reset_session_for_tests()
    cfg_module.set_config(cfg_module.MeditationConfig(postgres_url="postgresql://localhost/db"))
    url = _resolve_db_url()
    assert "asyncpg" in url
    cfg_module.reset_config()


def test_resolve_db_url_postgres_alias():
    from hushai.meditation.db.session import _resolve_db_url, reset_session_for_tests

    reset_session_for_tests()
    cfg_module.set_config(cfg_module.MeditationConfig(postgres_url="postgres://localhost/db"))
    url = _resolve_db_url()
    assert "postgresql+asyncpg" in url
    cfg_module.reset_config()


# ---------------------------------------------------------------------------
#  memory — _category_label & archive_old_memories
# ---------------------------------------------------------------------------


def test_category_label():
    from hushai.meditation.core.memory import _category_label

    assert _category_label("meditation_experience") == "冥想经历"
    assert _category_label("emotion_pattern") == "情绪模式"
    assert _category_label("unknown_category") == "unknown_category"


@pytest.mark.asyncio
async def test_archive_old_memories(meditation_session):
    from hushai.meditation.core.memory import archive_old_memories
    from hushai.meditation.db.models import Memory

    mem = Memory(
        user_id="user-archive-test",
        category="life_context",
        content="旧记忆",
        importance=0.1,
        status="active",
    )
    meditation_session.add(mem)
    await meditation_session.commit()

    count = await archive_old_memories(meditation_session, "user-archive-test")
    assert count == 0  # recent memory shouldn't be archived


@pytest.mark.asyncio
async def test_get_user_memories(meditation_session):
    from hushai.meditation.core.memory import get_user_memories
    from hushai.meditation.db.models import Memory

    mem = Memory(
        user_id="user-list-test",
        category="emotion_pattern",
        content="测试记忆内容",
        summary="测试摘要",
        importance=0.8,
        status="active",
    )
    meditation_session.add(mem)
    await meditation_session.commit()

    memories, total = await get_user_memories(meditation_session, "user-list-test")
    assert total == 1
    assert len(memories) == 1
    assert memories[0].content == "测试记忆内容"

    # with category filter
    memories2, total2 = await get_user_memories(
        meditation_session, "user-list-test", category="emotion_pattern"
    )
    assert total2 == 1

    # wrong category
    memories3, total3 = await get_user_memories(
        meditation_session, "user-list-test", category="goal_progress"
    )
    assert total3 == 0


# ---------------------------------------------------------------------------
#  config — MeditationConfig.from_env
# ---------------------------------------------------------------------------


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("MEDITATION_JWT_SECRET", "my-secret")
    monkeypatch.setenv("MEDITATION_PORT", "9000")
    monkeypatch.setenv("MEDITATION_DEBUG", "true")

    cfg = cfg_module.MeditationConfig.from_env()
    assert cfg.jwt_secret == "my-secret"
    assert cfg.port == 9000
    assert cfg.debug is True
