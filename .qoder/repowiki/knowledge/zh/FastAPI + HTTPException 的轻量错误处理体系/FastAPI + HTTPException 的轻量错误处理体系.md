---
kind: error_handling
name: FastAPI + HTTPException 的轻量错误处理体系
category: error_handling
scope:
    - '**'
source_files:
    - hushai/meditation/app.py
    - hushai/meditation/admin/auth.py
    - hushai/meditation/api/auth.py
    - hushai/meditation/api/chat.py
    - hushai/llm.py
    - hushai/meditation/core/engine.py
    - hushai/meditation/schemas.py
    - hushai/cli.py
---

## 1. 采用的系统/方法
- Web 层：基于 FastAPI，统一通过 `fastapi.HTTPException` 抛出业务错误（401/403/404/400/500），由框架自动序列化为 JSON。
- 限流异常：在应用入口注册 `slowapi.errors.RateLimitExceeded` 处理器，使用 slowapi 内置 `_rate_limit_exceeded_handler` 返回标准响应。
- LLM 调用层：对 OpenAI SDK 的多种异常（`APITimeoutError`、`AuthenticationError`、`RateLimitError`、`PermissionDeniedError`、`APIStatusError`、`OpenAIError`）进行捕获，转换为可读中文说明后以 `RuntimeError` 向上抛出，再由 API 层转为 500。
- CLI 层：顶层 `try/except Exception` 兜底打印并返回非零退出码。
- 数据库事务：核心引擎函数在 `async with factory()` 块内用 `try/finally` 或 `try/except` 包裹，失败时显式 `session.rollback()`，再重新抛出异常交由上层处理。
- 无全局自定义异常类：未定义统一的领域异常层次结构，也未实现全局 `app.add_exception_handler(Exception)` 兜底处理器。

## 2. 关键文件与位置
- 应用入口与全局异常注册：`hushai/meditation/app.py`
- 管理员认证与 CSRF 校验（HTTPException 集中点）：`hushai/meditation/admin/auth.py`
- 用户认证与 Bearer Token 解析（将 `RuntimeError` 转 401）：`hushai/meditation/api/auth.py`、`hushai/meditation/api/chat.py`
- LLM 调用与 OpenAI 异常映射：`hushai/llm.py`
- 对话核心引擎（事务回滚）：`hushai/meditation/core/engine.py`
- Pydantic 请求/响应模型（含 `ErrorResponse`）：`hushai/meditation/schemas.py`
- CLI 顶层异常兜底：`hushai/cli.py`

## 3. 架构与约定
- 分层职责清晰：
  - API 路由层负责参数校验（Pydantic）、鉴权（Depends）、以及把业务异常映射为 `HTTPException(status_code, detail=...)`。
  - 核心引擎层只做业务编排与数据持久化，遇到异常直接上抛，不吞异常；事务失败时先 rollback 再 raise。
  - 外部依赖（OpenAI SDK）在 `hushai.llm.chat_once` 中统一包装为 `RuntimeError`，避免下游感知第三方异常类型。
- 错误传播路径典型示例：
  - 认证失败：`verify_admin_token` / `get_current_user_id` → 抛出 `RuntimeError` → 路由层 `except RuntimeError as e: raise HTTPException(401, ...)`。
  - 资源不存在：各路由直接 `raise HTTPException(404, detail="...不存在")`。
  - 限流触发：slowapi 中间件抛出 `RateLimitExceeded` → app 注册的 handler 返回 429。
  - LLM 调用失败：OpenAI 异常 → `format_openai_error` → `RuntimeError` → 路由层 500。
- 前端/客户端错误体：`schemas.ErrorResponse` 提供 `{error, detail}` 结构，SSE 流式接口也按此格式发送错误 chunk。
- 安全相关错误（CSRF 失败、非管理员访问）统一返回 403/401，不泄露内部细节。

## 4. 开发者应遵循的规则
1. **Web 层只抛 `HTTPException`**：业务错误一律通过 `raise HTTPException(status_code=..., detail=...)` 表达，不要直接返回字符串或裸字典。
2. **外部依赖异常在边界转换**：调用 OpenAI、微信登录等外部服务时，捕获具体异常并转换为 `RuntimeError`（带中文提示），不要在路由层直接暴露第三方异常类型。
3. **事务失败必须回滚**：在 `core.engine` 风格的异步会话中，`try/except` 分支需先 `await session.rollback()` 再 `raise`，防止连接泄漏。
4. **鉴权错误走 401/403**：未登录、Token 无效、CSRF 失败等统一返回 401/403，detail 仅包含面向用户的简短信息。
5. **资源缺失用 404**：找不到记录时 `raise HTTPException(404, detail="xxx不存在")`，保持 detail 简洁可本地化。
6. **限流与全局异常**：新增全局异常处理器应在 `create_app` 中通过 `app.add_exception_handler` 注册；当前仅注册了 rate limit 处理器，如需统一 500 错误体可在该处扩展。
7. **CLI 顶层兜底**：命令行入口保留 `except Exception` 打印并返回非零码，便于脚本集成检测。