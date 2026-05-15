# hush.ai 质量修复设计文档

## 1. 需求概述

修复质量分析中识别的全部 13 项问题（3 项高优先级、4 项中优先级、3 项低优先级），并确保本地能打开项目运行。

## 2. 问题清单与修复方案

### 高优先级

#### 1.1 `chat_stream` 标题设置逻辑不一致
- **场景**：流式对话的标题取自 `prev_messages`（不含当前轮次用户消息），非流式版使用 `all_conv_messages`
- **影响**：首条用户消息恰好在当前轮时，流式对话标题为空
- **修复**：统一使用 `prev_messages + [assistant_msg]` 查找首条用户消息
- **文件**：`hushai/meditation/core/engine.py`
- **函数**：`chat_stream()`

#### 1.2 `chat_stream_endpoint` 未透传 `provider` 参数
- **场景**：`ChatRequest` 包含 `provider` 字段，但流式端点未传递
- **影响**：用户无法通过流式接口切换 LLM 提供商
- **修复**：在 `chat_stream()` 调用中加入 `provider=req.provider`
- **文件**：`hushai/meditation/api/chat.py`
- **函数**：`chat_stream_endpoint()`

#### 1.3 无事务回滚机制
- **场景**：用户消息已写入 DB，但 LLM 调用失败后无助手回复，产生"断头"消息
- **影响**：数据库中残留不完整对话记录
- **修复**：将 `user_msg` 写入、LLM 调用、`assistant_msg` 写入整体放在事务边界内。在 `chat_stream` 中，流式输出前写入用户消息，若 LLM 调用失败则回滚；在 `chat()` 中，整个流程在同一 session 内，已自然在事务边界。优化：增加显式 `session.rollback()` 在异常时。
- **文件**：`hushai/meditation/core/engine.py`
- **函数**：`chat()`, `chat_stream()`

#### 1.4 CORS 默认 `["*"]`
- **场景**：生产环境允许任意来源
- **影响**：CORS 安全风险
- **修复**：将 `cors_origins` 默认值改为空列表 `[]`，仅当 `debug=True` 时放宽为 `["*"]`
- **文件**：`hushai/meditation/config.py`
- **函数**：`MeditationConfig` dataclass

#### 1.5 缺少速率限制
- **场景**：聊天接口无 Rate Limiting
- **影响**：易被滥用，可能导致 API 费用激增
- **修复**：使用 `slowapi` 库添加基于内存的速率限制，为 `/api/chat/*` 设置合理阈值（如 30/min）
- **文件**：
  - `pyproject.toml`（添加 `slowapi>=0.1.9` 依赖）
  - `hushai/meditation/app.py`（注册 Limiter 中间件）
  - `hushai/meditation/api/chat.py`（为端点添加限制装饰器）

### 中优先级

#### 2.1 消息加载未分页
- **场景**：`_load_conversation_messages` 先加载全部历史再在 Python 中截断
- **影响**：长会话时数据库 IO 浪费
- **修复**：在 SQL 层面使用 `LIMIT` 替代全量加载后切片
- **文件**：`hushai/meditation/core/engine.py`
- **函数**：`_load_conversation_messages()`

#### 2.2 向量操作无错误隔离
- **场景**：`vector.add_memory_embedding()` 失败会导致整个对话流程异常
- **影响**：单个记忆向量写入失败阻断对话
- **修复**：在 `store_memories()` 中 `try/except` 包裹向量操作，仅记录日志
- **文件**：`hushai/meditation/core/memory.py`
- **函数**：`store_memories()`

#### 2.3 LLM 错误未分类处理
- **场景**：meditation 模块未像 CLI 模块那样将 OpenAI SDK 异常转换为用户友好的中文错误
- **影响**：原始异常可能泄漏到用户端
- **修复**：将 `hushai/llm.py:format_openai_error()` 复用到 meditation 模块的 `core/llm.py`
- **文件**：`hushai/meditation/core/llm.py`
- **函数**：`_get_client()`, `chat_completion()`, `chat_completion_stream()`

#### 2.4 记忆提取每次调用都执行
- **场景**：每轮对话都调用 LLM 提取记忆，成本高
- **影响**：API 费用与延迟累积
- **修复**：增加"隔轮提取"机制——仅在对话轮数为偶数时触发，或限制每会话最多提取 3 次
- **文件**：`hushai/meditation/core/engine.py`
- **函数**：`chat()`, `chat_stream()`

#### 2.5 JWT `iat` 使用 naive datetime
- **场景**：`iat` 字段未使用 timezone-aware datetime
- **影响**：某些严格库解析可能警告
- **修复**：使用 `datetime.now(timezone.utc)`（当前代码已正确使用，但需确认 `_create_token`）
- **文件**：`hushai/meditation/api/auth.py`
- **函数**：`_create_token()`

### 低优先级

#### 3.1 `MODE_SUFFIXES` 未包含 `"pua"`
- **修复**：在字典中添加 `"pua": ""` 保持逻辑一致（虽然不影响功能）
- **文件**：`hushai/llm.py`

#### 3.2 `get_memory_context_for_prompt` 重复生成前缀
- **修复**：移除函数内手写的前缀，改用 `MEMORY_SECTION` 模板，避免与 `prompt.py` 中拼接重复
- **文件**：`hushai/meditation/core/memory.py`
- **函数**：`get_memory_context_for_prompt()`

#### 3.3 `import_text` 中 chunk title 仅第一项有
- **修复**：为每个 chunk 都附加 title，增强检索上下文
- **文件**：`hushai/meditation/core/knowledge.py`
- **函数**：`import_text()`

## 3. 架构影响

- `pyproject.toml`：新增 `slowapi` 依赖（可选 meditation 组）
- `hushai/meditation/app.py`：新增 Limiter 注册
- 其余修改均为局部函数调整，无 API 破坏性变更

## 4. 边界条件与异常处理

- 速率限制异常应返回 HTTP 429，带 `Retry-After` 头
- 向量操作失败仅记录日志，不影响对话主流程
- 事务回滚在流式输出场景下：流式输出完成后才 commit，异常时自动回滚
- CORS 空列表时前端需同源部署或显式配置来源

## 5. 测试策略

- 为修复的每个问题添加或更新对应测试用例
- 确保现有测试（CLI + meditation core）全部通过
- 本地运行 `pytest` 验证

## 6. 本地打开

修复完成后，确保项目能在本地正常运行：
1. `make check` 通过（lint + typecheck + test）
2. `python -m hushai.meditation.app` 能启动服务
3. `hush hello` CLI 能正常响应
