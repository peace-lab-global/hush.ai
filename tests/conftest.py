"""pytest 公共 fixture。"""

from __future__ import annotations

from typing import Generator

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
