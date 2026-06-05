#!/usr/bin/env python3
"""兼容旧入口：直接调用产品化命令导入 open-cognition 知识库。"""

from hushai.meditation.commands.init_knowledge import main

if __name__ == "__main__":
    raise SystemExit(main())
