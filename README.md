<div align="center">

# hush.ai

```
0000001100010000000100011000000
0000011000100000000010001100000
0000011001000011100001001100000
0000010001000100010001000100000
0000010001001000001001000100000
0000010011001001001001100100000
0000010001001000001001000100000
0000010001000100010001000100000
0000011001000011100001001100000
0000011000100000000010001100000
0000001100010000000100011000000
```

**把噪音静下来。把答案收成一句话。**

[![CI](https://img.shields.io/github/actions/workflow/status/peace-lab-global/hush.ai/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white)](https://github.com/peace-lab-global/hush.ai/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/peace-lab-global/hush.ai?style=social)](https://github.com/peace-lab-global/hush.ai)
[![Issues](https://img.shields.io/github/issues/peace-lab-global/hush.ai)](https://github.com/peace-lab-global/hush.ai/issues)

[文档](#文档) · [安装](#安装) · [演示](#演示) · [了了冥想老师](#了了--冥想老师-ai-分身) · [配置](#配置) · [贡献](#贡献)

</div>

---

## 它是什么

`hush.ai` 包含两个产品：

| 产品 | 定位 |
|------|------|
| **hush CLI** | 终端禅意 AI，一句到底 |
| **了了 (LiaoLiao)** | 冥想老师 AI 分身 — 长期记忆 + RAG 知识库 + 语音对话 |

### hush CLI

`hush` 是一个运行在终端里的 **禅意 AI CLI**：只需配置 **`LLM_APPKEY`**（OpenAI 兼容 API），默认以「哲理老人」的口吻回答；并在本地把模型输出 **压成一句话**（句末标点切首句，否则取首行并截断），避免长篇大论。（**例外**：`pua` 模式使用独立演练提示，不叠用哲理老人基座，见下表与 [配置说明](docs/configuration.md)。）

内置多种 **对话模式**（默认 `calm`）：

| 模式 | 含义 |
|------|------|
| `calm` | **反焦虑**：接纳情绪、语气平稳、少命令式（默认） |
| `focus` | **反拖延**：小步行动、不羞辱、不堆清单 |
| `hype` | **打鸡血**：积极有力量，避免空洞口号 |
| `plain` | 仅保留基础「哲理老人」提示，不追加模式后缀 |
| `pua` | **反PUA 演练**：教育向、虚构情境，练习觉察与回应边界 |

---

## 为什么选择 hush.ai

|  |  |
|--|--|
| **一句到底** | CLI 模式强制单句输出，适合「点一下就走」的决策场景 |
| **了了冥想老师** | 有记忆的 AI 冥想陪伴 — 记住每位用户的状态、偏好、目标 |
| **长期记忆** | 7 大记忆维度，自动提取、向量检索、重要性评分、90 天自动归档 |
| **RAG 知识库** | 导入老师理论体系，语义搜索注入对话，让 AI 真正「学会」老师的方法 |
| **多模型路由** | OpenAI / DeepSeek / 智谱 一键切换，支持任意 OpenAI 兼容端点 |
| **语音对话** | 浏览器语音识别 + 语音合成，可配置音色、语速、音调 |
| **安全护栏** | 内置危机信号检测，自动建议专业求助渠道 |
| **多租户** | 每位用户独立记忆空间，微信小程序 OAuth 接入 |
| **全功能管理后台** | 用户、对话、记忆、知识库一站式管理 |

---

## 目录

- [安装](#安装)
- [hush CLI 演示](#hush-cli-演示)
- [了了 — 冥想老师 AI 分身](#了了--冥想老师-ai-分身)
  - [核心架构](#核心架构)
  - [长期记忆系统](#长期记忆系统)
  - [RAG 知识库](#rag-知识库)
  - [语音配置](#语音配置)
  - [管理后台](#管理后台)
  - [安全设计](#安全设计)
  - [快速启动](#快速启动)
  - [API 总览](#api-总览)
  - [配置项](#配置项)
- [hush CLI 配置](#hush-cli-配置)
- [贡献](#贡献)
- [许可证](#许可证)

---

## 安装

**环境：** Python **3.9+**

```bash
git clone https://github.com/peace-lab-global/hush.ai.git
cd hush.ai
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python3 -m pip install -U pip
python3 -m pip install -e .
```

**冥想老师额外依赖：**

```bash
python3 -m pip install -e ".[meditation]"
```

**Docker（可选，用于 PostgreSQL + ChromaDB）：**

```bash
docker compose up -d
```

---

## hush CLI 演示

**单次提问：**

```bash
export LLM_APPKEY='你的_API_Key'
hush "心很乱的时候，先做哪一件事？"
# → 先停三息，再决定下一步。
```

**管道：**

```bash
echo "今天最重要的是什么？" | hush
```

**交互：**

```bash
hush
# 提示符 > 下输入问题；exit / quit / q 退出
```

**反 PUA 演练：**

```bash
hush --mode pua "领导开会时当众说我太敏感，换一句他可能说的话"
```

| 场景 | 命令 |
|------|------|
| 单次 | `hush "问题"` |
| 管道 | `echo "问题" \| hush` |
| 交互 REPL | `hush` |
| 切换模式 | `hush --mode hype "冲一把"` 或 `export HUSH_MODE=focus` |
| 版本 | `hush --version` |

---

## 了了 — 冥想老师 AI 分身

> **每一次呼吸，都是回家的路。**

**了了 (LiaoLiao)** 是一个有长期记忆的冥想陪伴 AI — 她能记住每位用户的冥想经历、情绪模式、个人偏好和目标进展，让每次对话都建立在上次交流的基础上。

### 核心架构

```
┌──────────────────────────────────────────────┐
│                  前端 SPA                     │
│   SVG 头像 · 语音 I/O · 音色配置 · 萤火粒子    │
└─────────────┬────────────────────────────────┘
              │ SSE / REST
┌─────────────▼────────────────────────────────┐
│             FastAPI 服务层                     │
│  ┌──────┐ ┌──────┐ ┌───────┐ ┌────────────┐  │
│  │ Auth │ │ Chat │ │Memory │ │ Knowledge  │  │
│  └──┬───┘ └──┬───┘ └───┬───┘ └─────┬──────┘  │
│     │        │         │           │          │
│  ┌──▼────────▼─────────▼───────────▼───────┐  │
│  │          对话引擎 (Engine)                │  │
│  │  Prompt 构建 → LLM 调用 → 记忆提取       │  │
│  └──┬──────────┬──────────┬────────────────┘  │
│     │          │          │                    │
└─────┼──────────┼──────────┼────────────────────┘
      │          │          │
┌─────▼───┐ ┌───▼────┐ ┌──▼──────────┐
│PostgreSQL│ │ChromaDB│ │ LLM Router  │
│  /SQLite │ │ 向量库  │ │ OpenAI/DS/ZP│
└──────────┘ └────────┘ └─────────────┘
```

### 长期记忆系统

了了不只是聊天 — 她会从每次对话中 **自动提取** 关键信息，存入长期记忆，并在未来对话中 **智能检索** 相关记忆注入上下文。

**7 大记忆维度：**

| 类别 | 记录内容 |
|------|---------|
| 🧘 冥想经历 | 练习时长、频率、体感、技法偏好 |
| 💭 情绪模式 | 常见情绪、触发因素、变化趋势 |
| ✨ 个人偏好 | 引导风格、练习时间、沟通方式 |
| 🎯 目标进展 | 练习目标、里程碑、当前阶段 |
| 📌 重要事件 | 突破、领悟、困难、转折点 |
| 💊 健康提醒 | 身体限制、不适感、医嘱 |
| 🌏 生活背景 | 工作、家庭、压力来源 |

**记忆生命周期：**

1. **自动提取** — 每次对话后，LLM 自动从对话内容提取记忆（独立模型，低温 0.3）
2. **双重存储** — PostgreSQL 结构化存储 + ChromaDB 向量嵌入
3. **语义检索** — 基于当前消息的向量相似度搜索，注入系统提示
4. **重要性评分** — 0~1 分，影响检索排序和归档策略
5. **自动归档** — 90 天以上且重要性 < 0.3 的记忆自动归档

### RAG 知识库

导入冥想老师的理论体系，让 AI 真正「学会」老师的教学方法：

- **智能分块** — 800 字块 + 200 字重叠，中文优化的段落感知切分
- **层次导入** — 支持嵌套结构（章节/小节），保持知识体系完整性
- **语义搜索** — ChromaDB 余弦相似度检索，Top-K 结果注入提示
- **三种导入方式** — 文本导入、文件上传、结构化 JSON

```bash
# 导入知识文本
curl -X POST http://localhost:8000/api/knowledge/import \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "正念呼吸法", "content": "...", "tags": ["呼吸", "入门"]}'
```

### 语音配置

了了支持完整的 **语音输入 + 语音输出**：

- **语音输入** — 浏览器 Web Speech API，中文识别，说完自动发送
- **语音输出** — SpeechSynthesis TTS，每条回复可一键朗读
- **音色选择** — 从设备所有可用语音中选择，支持按性别/语言筛选
- **语速调节** — 0.5x ~ 2.0x 可调（默认 0.9x）
- **音调调节** — 0.5 ~ 2.0 可调（默认 1.1）
- **一键试听** — 调整后立即试听效果
- **持久化** — 所有设置自动保存到 localStorage

### 管理后台

完整的服务端渲染管理面板（`/admin/`）：

| 页面 | 功能 |
|------|------|
| 仪表盘 | 用户/对话/记忆/知识库统计，最近活动 |
| 用户管理 | 列表、搜索、启用/禁用、详情（对话+记忆） |
| 对话管理 | 列表、按用户筛选、查看完整消息记录 |
| 记忆管理 | 列表、按用户/分类筛选、删除 |
| 知识库管理 | 列表、搜索、导入、删除 |
| 系统设置 | 查看当前配置 |

### 安全设计

- **JWT 认证** — 7 天有效期，HS256 签名
- **多租户隔离** — 每位用户只能访问自己的记忆和对话
- **管理员独立认证** — Cookie-based，独立于用户 JWT
- **CORS 配置** — 可配置允许的来源域名
- **危机检测** — 自动识别自伤、严重焦虑/抑郁、暴力信号，引导专业求助
- **输入验证** — Pydantic 模型校验，消息长度限制 5000 字符

### 快速启动

**1. 最小化启动（SQLite，无需 Docker）：**

```bash
export MEDITATION_JWT_SECRET=your-secret
export MEDITATION_OPENAI_API_KEY=sk-your-key
python3 -m uvicorn hushai.meditation.app:get_app --factory
```

**2. 使用脚本启动：**

```bash
# SQLite 模式
bash scripts/start_server.sh

# PostgreSQL 模式
bash scripts/start_server.sh --postgresql
```

**3. Docker 全套：**

```bash
docker compose up -d                                    # 启动 PostgreSQL + ChromaDB
export MEDITATION_POSTGRES_URL=postgresql+asyncpg://hush:hush123@localhost:5432/hush_meditation
export MEDITATION_OPENAI_API_KEY=sk-your-key
export MEDITATION_JWT_SECRET=your-secret
python3 -m uvicorn hushai.meditation.app:get_app --factory
```

**访问：**

| 页面 | URL |
|------|-----|
| 对话页 | http://localhost:8000/ |
| API 文档 | http://localhost:8000/debug |
| ReDoc | http://localhost:8000/redoc |
| 管理后台 | http://localhost:8000/admin/ |
| 健康检查 | http://localhost:8000/health |

### API 总览

#### 对话

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/chat/` | 标准对话（请求/响应） |
| `POST` | `/api/chat/stream` | SSE 流式对话 |

#### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/dev-login` | 开发环境登录 |
| `POST` | `/api/auth/wx-login` | 微信小程序 OAuth |

#### 记忆

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/memory/` | 查看当前用户记忆列表 |

#### 知识库

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/knowledge/import` | 导入文本知识 |
| `POST` | `/api/knowledge/import-file` | 上传文件导入 |
| `POST` | `/api/knowledge/import-structured` | 导入结构化数据 |
| `POST` | `/api/knowledge/search` | 语义搜索知识库 |

#### 管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/admin/users` | 用户列表 |
| `GET` | `/api/admin/users/{id}/profile` | 用户详情 |

### 配置项

所有配置通过环境变量设置，统一 `MEDITATION_` 前缀：

**核心配置：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MEDITATION_JWT_SECRET` | — | JWT 签名密钥（**必填**） |
| `MEDITATION_OPENAI_API_KEY` | — | LLM API Key（**必填**） |
| `MEDITATION_POSTGRES_URL` | 空（SQLite） | PostgreSQL 连接串 |
| `MEDITATION_CHROMA_DIR` | 空（内存） | ChromaDB 持久化目录 |

**LLM 多模型：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MEDITATION_DEFAULT_LLM_PROVIDER` | `openai` | 默认 LLM 提供商 |
| `MEDITATION_DEFAULT_LLM_MODEL` | `gpt-4o-mini` | 默认模型 |
| `MEDITATION_OPENAI_BASE_URL` | OpenAI 官方 | OpenAI 端点 |
| `MEDITATION_DEEPSEEK_API_KEY` | — | DeepSeek API Key |
| `MEDITATION_ZHIPU_API_KEY` | — | 智谱 API Key |

**向量化：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MEDITATION_EMBEDDING_PROVIDER` | `openai` | Embedding 提供商 |
| `MEDITATION_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding 模型 |

**调优参数：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MEDITATION_MEMORY_TOP_K` | `5` | 记忆检索数量 |
| `MEDITATION_KNOWLEDGE_TOP_K` | `3` | 知识检索数量 |
| `MEDITATION_CONVERSATION_MAX_TURNS` | `20` | 对话历史轮次上限 |

**微信小程序：**

| 变量 | 说明 |
|------|------|
| `MEDITATION_WX_APPID` | 小程序 AppID |
| `MEDITATION_WX_SECRET` | 小程序 Secret |

**管理后台：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MEDITATION_ADMIN_USERNAME` | `admin` | 管理员用户名 |
| `MEDITATION_ADMIN_PASSWORD` | `admin` | 管理员密码 |

完整配置模板见 [`.env.example`](.env.example)。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 后端框架 | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) |
| 数据库 | PostgreSQL / SQLite |
| 向量数据库 | ChromaDB |
| LLM | OpenAI / DeepSeek / 智谱 (OpenAI 兼容协议) |
| 认证 | JWT (python-jose) + 微信 OAuth |
| 前端 | 原生 HTML/CSS/JS，SVG 头像 |
| 模板引擎 | Jinja2 (管理后台) |
| 测试 | pytest (69 tests passing) |
| 部署 | Docker Compose / uvicorn |

---

## 文档

| 文档 | 说明 |
|------|------|
| [docs/README.md](docs/README.md) | 文档中心入口 |
| [docs/configuration.md](docs/configuration.md) | hush CLI 环境变量、JSON 配置 |
| [docs/cli.md](docs/cli.md) | CLI 参数、管道、REPL、退出码 |
| [docs/architecture.md](docs/architecture.md) | 模块职责与请求流程 |
| [.env.example](.env.example) | 冥想老师完整配置模板 |

---

## hush CLI 配置

### LLM 接入说明

`hush` 使用 **OpenAI 官方 Python SDK** 调用 `chat.completions.create`，需要支持 OpenAI 兼容的端点。

```bash
export LLM_APPKEY='你的_API_Key'   # 勿提交到 git
hush "你好"
```

自建网关：

```bash
export LLM_APPKEY='…'
export OPENAI_BASE_URL='https://你的兼容网关/v1'
export LLM_MODEL='模型名'
hush "你好"
```

### 常用环境变量

| 变量 | 说明 |
|------|------|
| `LLM_APPKEY` | API Key |
| `OPENAI_BASE_URL` | 兼容网关 Base URL |
| `LLM_MODEL` | 模型名，默认 `gpt-4o-mini` |
| `LLM_TIMEOUT` | 超时（秒），默认 `60` |
| `HUSH_MODE` | `calm` / `focus` / `hype` / `plain` / `pua` |

### 使用速查

| 场景 | 命令 |
|------|------|
| 单次 | `hush "问题"` |
| 管道 | `echo "问题" \| hush` |
| 交互 REPL | `hush` |
| 切换模式 | `hush --mode hype "冲一把"` |
| 反 PUA 演练 | `hush --mode pua "…"` |
| 版本 | `hush --version` |

---

## 常见问题

<details>
<summary><strong>了了：如何开始？</strong></summary>

最简单的方式 — 无需 Docker，一条命令启动：

```bash
MEDITATION_JWT_SECRET=dev MEDITATION_OPENAI_API_KEY=sk-xxx \
  python3 -m uvicorn hushai.meditation.app:get_app --factory
```

打开 http://localhost:8000/ ，输入昵称即可开始对话。

</details>

<details>
<summary><strong>了了：支持哪些 LLM？</strong></summary>

所有提供 OpenAI 兼容 API 的服务商均可使用。内置支持 OpenAI、DeepSeek、智谱。切换只需设置环境变量 `MEDITATION_DEFAULT_LLM_PROVIDER`。

</details>

<details>
<summary><strong>了了：记忆存储在哪里？</strong></summary>

双重存储：PostgreSQL（或 SQLite）保存结构化数据（分类、重要性、状态），ChromaDB 保存向量嵌入用于语义检索。开发模式下可全部使用本地文件，无需外部服务。

</details>

<details>
<summary><strong>了了：如何导入老师的知识体系？</strong></summary>

三种方式：通过 API 导入文本、上传文件、导入结构化 JSON。系统会自动分块并向量化，在对话时通过语义搜索注入相关内容。详见 [API 总览 - 知识库](#api-总览)。

</details>

<details>
<summary><strong>hush CLI：提示未配置 API 密钥</strong></summary>

设置 `LLM_APPKEY`，或在配置文件中填写 `llm_appkey`。见 [配置文档](docs/configuration.md)。

</details>

<details>
<summary><strong>hush CLI：几种模式有什么区别？</strong></summary>

`calm`/`focus`/`hype` 在系统提示中追加不同前缀，`plain` 不加；`pua` 使用独立演练提示。详见 [docs/configuration.md](docs/configuration.md)。

</details>

---

## 测试

```bash
# 单元测试（69 tests）
python3 -m pytest tests/ -q

# 端到端测试（需启动服务）
python3 scripts/test_local.py

# Lint
python3 -m ruff check hushai/ tests/
```

---

## 贡献

我们欢迎 Issue 与 Pull Request。

```bash
pip install -e ".[dev]"
make check
```

流程与 CI 说明见 **[CONTRIBUTING.md](CONTRIBUTING.md)**。

---

## 社区、安全与许可证

| 资源 | 链接 |
|------|------|
| 行为准则 | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| 贡献指南 | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 安全披露 | [SECURITY.md](SECURITY.md) |
| 治理 | [GOVERNANCE.md](GOVERNANCE.md) |
| 维护者与发版 | [MAINTAINERS.md](MAINTAINERS.md) |
| 变更记录 | [CHANGELOG.md](CHANGELOG.md) |

**许可证：** [Apache License 2.0](LICENSE) · 归属见 [NOTICE](NOTICE)

---

## English

**hush.ai** includes two products:

1. **hush CLI** — A minimal terminal AI that outputs exactly **one sentence**. Modes: `calm` (anti-anxiety), `focus` (anti-procrastination), `hype` (motivational), `plain`, `pua` (educational boundary drill). Uses OpenAI-compatible Chat Completions.

2. **LiaoLiao (了了)** — An AI meditation teacher with **long-term memory**. Features include: 7-category memory extraction, RAG knowledge base, multi-LLM routing (OpenAI/DeepSeek/Zhipu), voice I/O with configurable timbre/speed/pitch, WeChat Mini Program OAuth, full admin dashboard, and safety guardrails with crisis detection.

```bash
# Quick start (SQLite, no Docker needed)
MEDITATION_JWT_SECRET=dev MEDITATION_OPENAI_API_KEY=sk-xxx \
  python3 -m uvicorn hushai.meditation.app:get_app --factory
# → http://localhost:8000/
```

| Resource | Link |
|----------|------|
| Documentation hub | [docs/README.md](docs/README.md) |
| CLI configuration | [docs/configuration.md](docs/configuration.md) |
| CLI reference | [docs/cli.md](docs/cli.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Security | [SECURITY.md](SECURITY.md) |
| Meditation env template | [.env.example](.env.example) |

**License:** [Apache-2.0](LICENSE)
