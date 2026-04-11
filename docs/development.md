# 开发文档（研发沉淀）

本文件用于沉淀项目研发过程中的功能边界、模块实现点、验证方法与质量要求，确保需求、实现与测试可追溯一致。

## 1. 目标范围

系统需具备并可验证以下核心能力：

- RAG（检索增强生成）：支持导入并集成检索组件；支持 Markdown 语料库；对话生成时自动检索并注入上下文以增强回答。
- Skills（技能插件）：支持导入与挂载技能模块；对话生成时自动挂载并调用已配置技能增强回答。
- 智能体配置管理：支持灵活的配置参数设置与运行时动态调整。
- 对话历史：运行时前台用户与智能体的所有对话必须完整保存，并支持可追溯查询。
- 工程质量：核心模块具备单元测试覆盖；接口文档齐全；错误处理机制完善；性能指标符合预期（至少具备可观测与可压测路径）。

## 2. 系统架构（实现落点）

### 2.1 分层结构

- 前端：静态 SPA（开发登录、语音 I/O）。
- API 服务：FastAPI 路由层，负责认证、对话、技能、知识库、管理接口。
- 引擎编排：对话引擎负责组装 system prompt（记忆 + 知识 + 历史 + 技能），调用 LLM，并在对话后抽取长期记忆。
- 数据存储：
  - PostgreSQL / SQLite：结构化存储用户、对话、消息、技能、知识分块、记忆条目。
  - ChromaDB：知识库与记忆的向量检索。

### 2.2 关键数据模型

参见：`hushai/meditation/db/models.py`

- `Conversation` / `Message`：对话与消息持久化（可追溯查询基础）。
- `Skill`：技能片段（注入 system prompt，支持启用/排序）。
- `KnowledgeChunk`：知识分块（支持 tags、source、parent 结构）。
- `Memory`：长期记忆（含 category、importance、状态与来源对话）。

## 3. RAG（知识库）模块

### 3.1 能力与约束

- 支持三种导入路径：
  - 文本导入（JSON）
  - 文件导入（上传文件）
  - 结构化导入（支持层级 children）
- 支持 Markdown：解析 YAML frontmatter（title/tags），将 Markdown 转为更适合向量化的纯文本，并自动附加 `markdown` 标签。
- 检索注入：对话时以用户当前 query 为检索条件，取 Top-K 片段拼接进 prompt。

对应实现：

- Markdown/导入预处理：`hushai/meditation/core/knowledge.py`
- 向量库接口：`hushai/meditation/db/vector.py`
- 对话引擎注入：`hushai/meditation/core/engine.py`
- API：`hushai/meditation/api/knowledge.py`

### 3.2 关键流程（文本导入）

1. 接收导入请求，识别 `content_format`（plain/markdown）。
2. 若为 markdown：
   - 解析 frontmatter → title/tags
   - Markdown → plain text（无额外依赖）
3. 分块：段落感知切分（chunk_size/overlap 可调）。
4. 写入数据库 `KnowledgeChunk`，并 upsert 到 Chroma collection `knowledge`。

### 3.3 验证要点

- Markdown 中链接/格式符号应在入库文本中被净化（避免 URL 噪声影响 embedding）。
- `KnowledgeChunk` 与 Chroma 中的 ids 一致可追溯。
- `top_k` 与配置一致（默认读取 `MEDITATION_KNOWLEDGE_TOP_K`）。

## 4. Skills（技能插件）模块

### 4.1 能力与约束

- 可批量导入技能（JSON / 文件上传），保存为 `Skill` 实体。
- 对话时可挂载技能上下文，作为 system prompt 的技能区块注入。
- 运行时技能注入上限：每轮对话最多注入 `MAX_SKILLS_PER_MESSAGE` 条。

对应实现：

- 技能上下文构建：`hushai/meditation/core/skills.py`
- 技能导入/列表 API：`hushai/meditation/api/skills.py`
- 管理后台页面：`hushai/meditation/admin/router.py` + templates

### 4.2 自动挂载策略

- 当 `skill_ids` 明确传入：
  - 仅加载指定 ids（去重、按 sort_order/name 排序），并只加载启用的技能。
- 当 `skill_ids` 为 `None`：
  - 自动加载所有启用技能（按 sort_order/name 排序，截断到上限）。
- 当 `skill_ids` 为空数组：
  - 不挂载技能（返回空）。

该策略用于满足“智能体生成回答时能够自动挂载并调用已配置 skills 插件”的功能要求，并允许前端显式关闭技能注入。

## 5. 智能体配置管理（动态调整）

### 5.1 配置来源与作用域

实现位于 `hushai/meditation/config.py`：

- `MeditationConfig.from_env()`：从环境变量加载配置。
- `get_config()`：读取全局缓存配置（进程内）。
- `set_config()`：运行时更新进程内配置（动态生效）。
- `reset_config()`：测试/重置用途。

### 5.2 管理后台动态配置

管理后台提供运行参数的动态调整入口（进程内生效）：

- 页面：`/admin/settings`
- 路由：`hushai/meditation/admin/router.py`
- 模板：`hushai/meditation/admin/templates/settings.html`

支持动态调整的关键项（示例）：

- 默认 LLM provider / model
- 记忆检索 Top-K、知识检索 Top-K、上下文轮数上限
- provider API Key / base url（用于开发/调试；生产建议仍以环境变量或密钥管理为主）

注意：该能力属于“运行时动态调整（进程级）”。若需要“跨进程/跨重启持久化配置”，需引入 DB 配置表或配置中心并补充迁移与回滚策略。

## 6. 对话历史（保存与追溯）

### 6.1 保存位置与写入时机

对话引擎负责持久化写入：

- 用户消息：先写入 `Message(role='user')`
- LLM 回复后写入：`Message(role='assistant')`
- 对话元数据：`Conversation.title`/`updated_at` 等

实现：`hushai/meditation/core/engine.py`

### 6.2 可追溯查询

可通过管理后台查询与回溯：

- `/admin/conversations`：对话列表
- `/admin/conversations/{id}`：对话详情（按时间排序展示所有消息）

实现：`hushai/meditation/admin/router.py` + templates

## 7. 错误处理与接口文档

### 7.1 API 错误处理策略

- 认证失败统一返回 401（FastAPI `HTTPException`）。
- 引擎/LLM 等运行错误捕获后返回 500，避免泄露敏感信息。
- SSE 流式接口在异常时以 `ErrorResponse` 结构输出最后一条事件。

示例实现：`hushai/meditation/api/chat.py`

### 7.2 接口文档

FastAPI 默认提供：

- Swagger：`/debug`
- ReDoc：`/redoc`

管理后台 settings 页面提供快速链接。

## 8. 单元测试与验证

### 8.1 测试覆盖范围（核心模块）

现有测试主要覆盖：

- prompt 构建与拼装
- Markdown 导入预处理
- 知识分块策略
- 记忆抽取 JSON 解析逻辑
- bearer token 解析
- Skills 自动挂载逻辑

测试文件：`tests/meditation/test_core.py`

### 8.2 本地运行测试（推荐）

macOS/Homebrew Python 环境下建议使用 venv：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[meditation,dev]"
python3 -m pytest tests/ -q
```

## 9. 性能指标（建议的验收方式）

当前系统具备以下可观测/可压测入口（建议作为验收基线）：

- 对话接口：`POST /api/chat/`、`POST /api/chat/stream`
- 知识检索：`POST /api/knowledge/search`

建议的基线指标（按部署环境定义，需在 CI 或部署后做实测并记录）：

- P95 响应时间（非流式 / 流式首 token）
- 向量检索耗时（Chroma query）
- DB 写入耗时（消息写入、分块导入）
- 并发下错误率与资源占用（CPU/内存）

## 10. 研发 Checklist（交付门槛）

- 核心功能：RAG 导入/检索/注入、Skills 导入/挂载、动态配置、对话持久化与追溯均可演示与回归。
- 测试：核心模块单元测试通过；新增功能必须补测试。
- 文档：API 路由与请求响应模型在 FastAPI 文档可见；开发文档（本文件）与根 README 保持一致。
- 安全：不记录/不输出密钥；错误信息不泄露敏感上下文。
