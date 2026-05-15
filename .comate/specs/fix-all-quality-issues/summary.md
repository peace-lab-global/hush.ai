# hush.ai 质量修复总结

## 修复概览

本次修复覆盖了质量分析中识别的全部 13 项问题，分为 12 个任务执行，所有任务均已完成。

## 已修复问题清单

### 高优先级

1. **`chat_stream` 标题逻辑不一致** (`engine.py`)
   - 流式与非流式版本统一使用 `all_conv_messages` 查找首条用户消息

2. **`chat_stream_endpoint` 未透传 `provider` 参数** (`api/chat.py`, `schemas.py`)
   - 在 `ChatRequest` 中新增 `provider` 字段
   - `chat_endpoint` 和 `chat_stream_endpoint` 均透传 `provider=req.provider`

3. **无事务回滚机制** (`engine.py`)
   - `chat()` 增加外层 `try/except`，异常时显式 `session.rollback()`
   - `chat_stream()` 增加 `committed` 标志与 `finally` 块，未提交时自动回滚

4. **CORS 默认 `["*"]`** (`config.py`, `app.py`)
   - `MeditationConfig.cors_origins` 默认值改为 `[]`
   - `debug=True` 时才放宽为 `["*"]`

5. **缺少速率限制** (`pyproject.toml`, `app.py`, `api/chat.py`)
   - 新增 `slowapi` 依赖
   - 注册 `Limiter` 与 `RateLimitExceeded` 异常处理器
   - 聊天端点限制 `30/minute`

### 中优先级

6. **消息加载未分页** (`engine.py`)
   - `_load_conversation_messages` 改用 SQL `LIMIT` 替代全量加载后切片

7. **向量操作无错误隔离** (`memory.py`)
   - `store_memories()` 中 `try/except` 包裹 `vector.add_memory_embedding()`
   - 失败仅记录日志，不阻断对话主流程

8. **LLM 错误未分类处理** (`meditation/core/llm.py`)
   - 复用 `hushai.llm.format_openai_error()`
   - `chat_completion()` 和 `chat_completion_stream()` 捕获 `OpenAIError` 并转换为用户友好的中文错误

9. **记忆提取每次调用都执行** (`engine.py`)
   - 增加"偶数轮提取"机制：仅当用户消息数为偶数时才触发记忆提取，降低 API 调用成本

10. **JWT `iat` 使用 naive datetime** (`api/auth.py`)
    - 经确认，现有代码已正确使用 `datetime.now(timezone.utc)`，无需修改

### 低优先级

11. **`MODE_SUFFIXES` 未包含 `"pua"`** (`llm.py`)
    - 添加 `"pua": ""` 保持逻辑一致

12. **`get_memory_context_for_prompt` 重复生成前缀** (`memory.py`)
    - 移除函数内手写前缀，避免与 `prompt.py` 中 `MEMORY_SECTION` 模板重复

13. **`import_text` 中 chunk title 仅第一项有** (`knowledge.py`)
    - 每个 chunk 均附加 title，增强检索上下文

## 本地验证结果

- **Lint**: `ruff check` 全部通过
- **Format**: `ruff format` 全部通过
- **Tests**: `pytest` 73 个测试全部通过
- **CLI**: `hush --version` 正常响应
- **Web 服务**: `create_app()` 正常创建，服务启动于 `http://localhost:8002`，健康检查返回 `{"status":"ok"}`

## 已知遗留

- `mypy` 存在 22 个类型错误，均为原始代码遗留问题（`admin/router.py` 隐式 Optional、`vector.py` 类型不匹配等），本次修改未引入新的类型错误
