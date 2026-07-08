---
kind: logging_system
name: 基于 Python 标准 logging 的轻量日志系统
category: logging_system
scope:
    - '**'
source_files:
    - hushai/meditation/app.py
    - hushai/meditation/core/engine.py
    - hushai/meditation/core/llm.py
    - hushai/meditation/core/memory.py
    - hushai/meditation/core/remote_knowledge.py
    - hushai/meditation/core/wechat_pay.py
    - hushai/meditation/db/migrations/env.py
---

本仓库采用 Python 标准库 `logging` 作为唯一日志框架，未引入 loguru、structlog 等第三方方案。日志系统在 FastAPI 应用启动时集中配置，各模块通过 `logging.getLogger(__name__)` 获取命名 logger，形成以包路径为层级的树状结构。

## 1. 系统/工具
- 框架：Python 标准库 `logging`
- 输出格式：`%(asctime)s %(levelname)s %(name)s: %(message)s`
- 级别策略：由配置项 `cfg.debug` 决定 — debug 模式使用 `DEBUG`，生产使用 `INFO`
- 无结构化字段（JSON）输出，无独立 sink 路由或分级文件输出

## 2. 关键文件
- `hushai/meditation/app.py` — 在 `lifespan` 中调用 `logging.basicConfig` 完成全局初始化，并定义根 logger `hushai.meditation`
- `hushai/meditation/core/engine.py` — 主引擎 logger，记录记忆提取失败等核心流程事件
- `hushai/meditation/core/llm.py` — LLM 调用与 fallback 日志
- `hushai/meditation/core/memory.py` — 记忆提取/写入异常日志
- `hushai/meditation/core/remote_knowledge.py` — 远程知识源同步错误日志
- `hushai/meditation/core/wechat_pay.py` — 微信支付下单/查询错误日志
- `hushai/meditation/db/migrations/env.py` — Alembic 迁移通过 `fileConfig` 加载外部配置文件

## 3. 架构与约定
- **单点初始化**：所有日志配置集中在 `app.lifespan` 的 `basicConfig`，确保 uvicorn 进程启动后统一生效；`run()` 通过 `factory=True` 避免重复初始化。
- **命名空间分层**：logger 名称遵循包路径（如 `hushai.meditation.counseling`、`hushai.meditation.wechat_pay`），便于按模块过滤。
- **级别使用惯例**：
  - `info`：服务生命周期事件（启动、关闭、默认数据创建）、成功操作（导入成功、支付成功）
  - `warning`：可恢复异常（LLM provider 失败、记忆提取 JSON 解析失败、抓取失败）
  - `error`：不可恢复错误（Coze API 返回错误、微信下单失败、提交失败）
  - 异常堆栈统一通过 `exc_info=True` 附加
- **无请求级日志中间件**：未发现 Starlette/FastAPI request logging middleware，HTTP 访问日志依赖 uvicorn 默认输出。
- **Alembic 集成**：迁移脚本通过 `logging.config.fileConfig` 读取 alembic.ini 中的日志配置，与运行时 `basicConfig` 互不干扰。

## 4. 开发者应遵守的规则
- 始终使用 `import logging; logger = logging.getLogger(__name__)` 获取模块 logger，不要直接调用 `logging.info` 等顶层函数。
- 仅在业务关键路径上记录 `info`，将可预期且非致命的异常归入 `warning`，严重错误用 `error` 并附带 `exc_info=True`。
- 不要在循环或高频路径中使用 `debug`，以免在生产环境产生大量 I/O。
- 如需新增结构化字段（如 user_id、conversation_id），应在当前 `basicConfig` 的 format 中扩展占位符，而非改用第三方框架。
- 新增子模块时，logger 名称自然继承 `hushai.meditation.<module>` 层级，无需额外注册。