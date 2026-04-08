#!/usr/bin/env python3
"""一键本地测试 — 无需外部服务（SQLite + 内存 ChromaDB）。

用法:
    pip install -e ".[meditation]" aiosqlite greenlet eval_type_backport
    export MEDITATION_OPENAI_API_KEY=sk-your-key
    python3 scripts/test_local.py
"""

from __future__ import annotations

import subprocess
import sys
import time

import httpx

BASE = "http://127.0.0.1:8000"
ENV = {
    "MEDITATION_OPENAI_API_KEY": "test",
    "MEDITATION_JWT_SECRET": "dev-secret",
    "MEDITATION_DEBUG": "true",
}


def main() -> None:
    import os

    env = os.environ.copy()
    env.update(ENV)

    print("1. 启动冥想老师服务...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "hushai.meditation.app"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    try:
        run_tests()
    finally:
        proc.terminate()
        proc.wait(timeout=5)
        print("\n服务已关闭")


def run_tests() -> None:

    with httpx.Client(timeout=10.0) as client:
        print("2. 等待服务就绪...", end=" ", flush=True)
        for _ in range(40):
            try:
                r = client.get(f"{BASE}/health")
                if r.status_code == 200:
                    break
            except httpx.ConnectError:
                pass
            time.sleep(0.5)
        else:
            print("FAILED")
            return
        print("OK")

        r = client.get(f"{BASE}/docs")
        print(f"3. Swagger UI: {r.status_code == 200 and 'OK' or 'FAIL'}")

        r = client.post(f"{BASE}/api/auth/wx-login", json={"code": "test"})
        if r.status_code == 200:
            token = r.json()["access_token"]
            uid = r.json()["user_id"]
            print(f"4. 微信登录: OK (user={uid[:8]})")
        else:
            token, uid = create_test_user()
            print(f"4. 直接注入: OK (user={uid[:8]})")

        h = {"Authorization": f"Bearer {token}"}

        r = client.post(
            f"{BASE}/api/knowledge/import",
            headers=h,
            json={
                "content": (
                    "观呼吸法是佛教禅修中最基础的练习。\n\n"
                    "步骤：\n1. 安静场所盘腿坐\n2. 自然呼吸\n"
                    "3. 注意力放鼻尖感受呼吸\n4. 走神时温柔带回\n"
                    "5. 从5分钟开始逐渐延长\n\n"
                    "注意：不追求无念，走神即正念。"
                ),
                "title": "观呼吸入门",
                "tags": ["冥想", "入门"],
            },
        )
        ok = r.status_code == 200
        print(f"5. 导入知识: {'OK' if ok else 'FAIL'}")

        r = client.post(
            f"{BASE}/api/knowledge/search",
            headers=h,
            json={"query": "如何冥想", "top_k": 3},
        )
        n = len(r.json().get("results", [])) if r.status_code == 200 else 0
        print(f"6. 搜索知识: {n} 条结果")

        r = client.post(
            f"{BASE}/api/chat/",
            headers=h,
            json={"message": "老师你好，我没冥想过，从哪开始？"},
        )
        if r.status_code == 200:
            d = r.json()
            cid = d["conversation_id"]
            print("7. 对话: OK")
            print(f"   回复: {d['reply'][:60]}...")

            r2 = client.post(
                f"{BASE}/api/chat/",
                headers=h,
                json={
                    "message": "试了五分钟全是杂念",
                    "conversation_id": cid,
                },
            )
            print(f"8. 继续对话: {'OK' if r2.status_code == 200 else 'FAIL'}")
        else:
            print(f"7. 对话: 需要 LLM Key ({r.status_code})")

        r = client.get(f"{BASE}/api/memory/", headers=h)
        total = r.json()["total"] if r.status_code == 200 else 0
        print(f"9. 记忆: {total} 条")

    print("\n=== 本地测试完成 ===")


def create_test_user() -> tuple[str, str]:
    import uuid

    from hushai.meditation.api.auth import _create_token
    from hushai.meditation.db.models import User
    from hushai.meditation.db.session import get_session_factory

    factory = get_session_factory()

    async def _do():
        async with factory() as s:
            u = User(id=str(uuid.uuid4()), nickname="测试", wx_openid="test_dev")
            s.add(u)
            await s.commit()
            return u.id

    import asyncio

    uid = asyncio.get_event_loop().run_until_complete(_do())
    return _create_token(uid), uid


if __name__ == "__main__":
    main()
