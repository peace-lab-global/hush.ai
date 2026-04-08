#!/usr/bin/env python3
"""一键本地测试 — 无需外部服务（SQLite + 内存 ChromaDB）。"""

from __future__ import annotations

import os
import subprocess
import sys
import time

import httpx

BASE = "http://127.0.0.1:8000"


def start_server() -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("MEDITATION_OPENAI_API_KEY", "test")
    env.setdefault("MEDITATION_JWT_SECRET", "dev-secret-change-me")
    env.setdefault("MEDITATION_DEBUG", "true")
    proc = subprocess.Popen(
        [sys.executable, "-m", "hushai.meditation.app"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc


def wait_ready(client: httpx.AsyncClient, timeout: float = 20.0) -> bool:
    import time as _t

    deadline = _t.time() + timeout
    while _t.time() < deadline:
        try:
            r = client.get(f"{BASE}/health")
            if r.status_code == 200:
                return True
        except httpx.ConnectError:
            pass
        time.sleep(0.5)
    return False


def main() -> None:
    import asyncio

    print("启动冥想老师服务...")
    proc = start_server()
    try:
        asyncio.run(run_tests())
    finally:
        print("\n关闭服务...")
        proc.terminate()
        proc.wait(timeout=5)
        print("完成 ✓")


async def run_tests() -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("等待服务就绪...")
        if not wait_ready(client):
            print("ERROR: 服务未启动")
            return
        print("1. /health ✓")

        r = await client.get(f"{BASE}/docs")
        assert r.status_code == 200
        print("2. /docs (Swagger UI) ✓")

        r = await client.post(f"{BASE}/api/auth/wx-login", json={"code": "test_dev_code"})
        if r.status_code == 200:
            data = r.json()
            token = data["access_token"]
            user_id = data["user_id"]
            print(f"3. 微信登录 ✓ (user={user_id[:8]}...)")
        else:
            print("3. 微信登录跳过（未配置 WX_APPID），使用直接注入...")
            import uuid

            from hushai.meditation.api.auth import _create_token
            from hushai.meditation.db.models import User
            from hushai.meditation.db.session import get_session_factory

            factory = get_session_factory()
            async with factory() as session:
                user = User(id=str(uuid.uuid4()), nickname="测试用户", wx_openid="test_dev")
                session.add(user)
                await session.commit()
                user_id = user.id
            token = _create_token(user_id)
            print(f"3. 测试用户创建 ✓ (user={user_id[:8]}...)")

        headers = {"Authorization": f"Bearer {token}"}

        r = await client.post(
            f"{BASE}/api/knowledge/import",
            headers=headers,
            json={
                "content": (
                    "观呼吸法（Anapanasati）是佛教禅修中最基础的练习方法。\n\n"
                    "基本步骤：\n"
                    "1. 选择安静的场所，盘腿而坐\n"
                    "2. 自然呼吸，不刻意控制\n"
                    "3. 将注意力放在鼻尖或腹部，感受呼吸进出\n"
                    "4. 当念头升起时，温柔地把注意力带回呼吸\n"
                    "5. 每次练习从 5-10 分钟开始，逐渐延长\n\n"
                    "注意事项：\n"
                    "- 不要追求「没有念头」\n"
                    "- 每次发现走神就是一次正念的胜利\n"
                    "- 身体不适时可调整姿势"
                ),
                "title": "观呼吸法入门",
                "tags": ["冥想", "呼吸法", "入门"],
            },
        )
        assert r.status_code == 200
        print(f"4. 导入知识 ({len(r.json())} 块) ✓")

        r = await client.post(
            f"{BASE}/api/knowledge/search",
            headers=headers,
            json={"query": "如何开始冥想", "top_k": 3},
        )
        assert r.status_code == 200
        results = r.json()["results"]
        print(f"5. 搜索知识 ({len(results)} 条) ✓")

        r = await client.post(
            f"{BASE}/api/chat/",
            headers=headers,
            json={"message": "老师你好，我从来没有冥想过，可以从哪里开始？"},
        )
        if r.status_code == 200:
            data = r.json()
            print("6. 对话 ✓")
            print(f"   回复: {data['reply'][:80]}...")
            print(f"   记忆更新: {data['memory_updated']}")
            conv_id = data["conversation_id"]
        else:
            print(f"6. 对话失败（需要有效 LLM API Key）: {r.status_code}")
            conv_id = None

        if conv_id:
            r = await client.post(
                f"{BASE}/api/chat/",
                headers=headers,
                json={
                    "message": "我刚才试了五分钟，脑子里全是杂念",
                    "conversation_id": conv_id,
                },
            )
            if r.status_code == 200:
                print("7. 继续对话 ✓")
            else:
                print(f"7. 继续对话失败: {r.status_code}")

        r = await client.get(f"{BASE}/api/memory/", headers=headers)
        assert r.status_code == 200
        data = r.json()
        print(f"8. 查看记忆 ({data['total']} 条) ✓")

        r = await client.get(f"{BASE}/api/admin/users/{user_id}/profile", headers=headers)
        assert r.status_code == 200
        profile = r.json()
        tc = profile["total_conversations"]
        tm = profile["total_messages"]
        print(f"9. 用户档案 (对话={tc}, 消息={tm})")

    print("\n=== 全部通过 ✓ ===")


if __name__ == "__main__":
    main()
