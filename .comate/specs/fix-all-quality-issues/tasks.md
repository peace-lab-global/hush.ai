# hush.ai 质量修复任务计划

- [x] Task 1: 修复 `chat_stream` 标题逻辑不一致
    - 1.1: 将流式标题查找改为使用 `prev_messages + [assistant_msg]` 而非仅 `prev_messages`
    - 1.2: 验证非流式与流式版本逻辑一致

- [x] Task 2: 修复 `chat_stream_endpoint` 未透传 provider 参数
    - 2.1: 在 `api/chat.py` 流式端点调用 `chat_stream()` 时传入 `provider=req.provider`

- [x] Task 3: 添加数据库事务回滚机制
    - 3.1: 在 `chat()` 中增加显式 `session.rollback()` 异常处理
    - 3.2: 在 `chat_stream()` 中增加显式 `session.rollback()` 异常处理

- [x] Task 4: 收紧 CORS 默认配置
    - 4.1: 将 `MeditationConfig.cors_origins` 默认值从 `["*"]` 改为 `[]`
    - 4.2: 在 `app.py` 中 `debug=True` 时放宽为 `["*"]`

- [x] Task 5: 添加 API 速率限制
    - 5.1: 在 `pyproject.toml` 的 `meditation` 依赖组中添加 `slowapi>=0.1.9`
    - 5.2: 在 `app.py` 中注册 `SlowAPIMiddleware` 与内存限流器
    - 5.3: 在 `api/chat.py` 中为聊天端点添加 `@limiter.limit()` 装饰器

- [x] Task 6: 优化消息加载分页
    - 6.1: 在 `_load_conversation_messages()` 中改用 SQL `LIMIT` 替代全量加载后切片

- [x] Task 7: 隔离向量操作异常
    - 7.1: 在 `store_memories()` 中 `try/except` 包裹 `vector.add_memory_embedding()`
    - 7.2: 异常时仅记录 `logger.warning`，不阻断主流程

- [x] Task 8: 统一 LLM 错误处理
    - 8.1: 将 `hushai/llm.py:format_openai_error()` 复用到 `meditation/core/llm.py`
    - 8.2: 在 `chat_completion()` 和 `chat_completion_stream()` 中捕获 OpenAIError 并转换

- [x] Task 9: 记忆提取节流机制
    - 9.1: 在 `chat()` 和 `chat_stream()` 中仅在对话轮数为偶数时触发记忆提取

- [x] Task 10: 修复 JWT `iat` 与低优先级问题
    - 10.1: 确认 `_create_token` 中 `iat` 使用 `datetime.now(timezone.utc)`
    - 10.2: 在 `llm.py` `MODE_SUFFIXES` 中添加 `"pua": ""`
    - 10.3: 修复 `get_memory_context_for_prompt` 前缀重复问题
    - 10.4: 修复 `import_text` 中每个 chunk 都附加 title

- [x] Task 11: 更新与补充测试
    - 11.1: 为修复的每个问题添加对应单元测试
    - 11.2: 运行 `pytest` 确保全部通过

- [x] Task 12: 本地验证与打开
    - 12.1: 运行 `make check`（lint + typecheck + test）
    - 12.2: 验证 CLI `hush hello` 正常响应
    - 12.3: 验证 Web 服务能正常启动
