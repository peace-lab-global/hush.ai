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

</div>

---

## 1. 产品概述

`hush.ai` 是一款面向现代生活压力的智能化心理与冥想陪伴系统。它通过集成大语言模型（LLM）技术，提供两类核心产品：

| 产品 | 说明 |
|------|------|
| **hush CLI** | 极简禅意终端工具，支持多种心理调节模式，每次仅输出一句话，帮助用户快速决策与平复心情。 |
| **小观 (XiaoGuan)** | 具备长期记忆与专业知识储备的 AI 冥想陪伴。支持多角色切换、呼吸练习、冥想追踪与语音交互。 |

---

## 2. 核心功能

### 2.1 冥想搭子（AI 角色切换）

可选择不同风格的冥想导师进行对话：

| 导师 | 风格标签 | 音色 |
|------|----------|------|
| 小观 | 温柔、日常正念、压力缓解 | 女声 |
| 禅师 | 禅宗、公案、觉悟 | 男声 |
| 森林派大师 | 森林禅、身体觉察、自然 | 男声 |
| 藏传上师 | 藏传、慈悲、止观 | 女声 |
| 道家真人 | 道家、无为、自然 | 男声 |

### 2.2 冥想追踪

- **情绪签到**：每次冥想前后记录情绪状态（1-10 分）
- **进度统计**：总冥想次数、总练习分钟、连续天数、平均情绪
- **本周进度**：可视化展示每日冥想情况

### 2.3 呼吸练习

内置三种呼吸法引导：

- **4-7-8 呼吸**：放松与入睡
- **方形呼吸**：专注力训练
- **平静呼吸**：日常减压

### 2.4 RAG 知识增强

- 导入 Markdown 格式语料库（支持 YAML frontmatter）
- 段落感知分块与向量化存储
- 对话时自动检索相关理论辅助回答

### 2.5 Skills 技能插件

- 模块化技能系统，支持动态导入与挂载
- 智能体自动根据配置调用技能增强回复
- 支持批量导入（JSON / 文件上传）

### 2.6 长期记忆系统

自动从对话中提取 7 大维度的记忆：

- 冥想经历、情绪模式、个人偏好
- 目标进展、重要事件、健康备注、生活背景

### 2.7 语音交互

- **语音输入**：Web Speech API 实时识别
- **语音合成**：可选音色、语速、音调
- **流式朗读**：支持边生成边朗读

### 2.8 安全护栏

- 内置危机信号检测
- 自动识别敏感词并提供专业求助建议

---

## 3. 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前台 (index.html)                       │
│   冥想搭子 · 呼吸练习 · 进度追踪 · 语音 I/O · 流式对话   │
└──────────────────────────┬──────────────────────────────────┘
                           │ JWT Bearer + Refresh Token
┌──────────────────────────▼──────────────────────────────────┐
│                      FastAPI 服务层                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ /api/chat│ │/api/auth │ │/api/skills│ │/api/memory│    │
│  │ /stream  │ │/refresh │ │           │ │          │    │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘    │
│       │              │            │            │             │
│  ┌────▼────────────▼────────────▼────────────▼────┐       │
│  │              Engine (核心编排层)                 │       │
│  │  提示词构建 · 知识检索 · 记忆提取 · 技能挂载   │       │
│  │  导师选择 · 安全过滤 · 危机检测               │       │
│  └────────────────────┬───────────────────────────┘       │
│                       │                                    │
│  ┌────────────────────▼───────────────────────────┐        │
│  │              LLM 适配层                         │        │
│  │     OpenAI · DeepSeek · 智谱 · Kimi          │        │
│  │     (自动降级策略)                              │        │
│  └───────────────────────────────────────────────┘        │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
    PostgreSQL          ChromaDB          静态文件
    (关系数据)         (向量检索)        (Admin)
```

---

## 4. 目录结构

```
hush.ai/
├── hushai/
│   └── meditation/
│       ├── api/                    # API 路由
│       │   ├── admin.py           # 管理后台 API
│       │   ├── auth.py           # 认证 API
│       │   ├── chat.py           # 对话 API（含 SSE 流式）
│       │   ├── frontend.py       # 前台认证 API
│       │   ├── knowledge.py      # 知识库 API
│       │   ├── login.py          # 登录 API
│       │   ├── meditation.py     # 冥想追踪 API
│       │   ├── memory.py         # 记忆 API
│       │   ├── skills.py         # 技能插件 API
│       │   └── teachers.py       # 冥想搭子 API
│       ├── core/                  # 核心业务逻辑
│       │   ├── engine.py         # 对话引擎
│       │   ├── knowledge.py      # 知识库处理
│       │   ├── llm.py            # LLM 适配层
│       │   ├── memory.py         # 记忆提取与存储
│       │   ├── prompt.py         # 提示词构建
│       │   ├── safety.py         # 安全过滤
│       │   ├── scenes.py         # 场景管理
│       │   └── skills.py         # 技能插件
│       ├── db/                    # 数据库层
│       │   ├── models.py         # SQLAlchemy 模型
│       │   ├── session.py        # 会话管理
│       │   └── vector.py         # ChromaDB 接口
│       ├── admin/                 # 管理后台
│       │   ├── router.py        # 管理路由
│       │   ├── auth.py          # 管理员认证
│       │   ├── audit.py         # 审计日志
│       │   ├── export.py        # 数据导出
│       │   └── templates/        # Jinja2 模板
│       └── static/               # 前台静态资源
│           └── index.html        # 前台 SPA
├── tests/                        # 单元测试
├── docs/                         # 文档
├── scripts/                      # 启动脚本
└── knowledge/                   # 知识库语料
```

---

## 5. API 概览

### 5.1 认证

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/dev-login` | POST | 开发模式登录（昵称即可） |
| `/api/auth/refresh` | POST | 刷新 Access Token |

### 5.2 对话

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/chat/` | POST | 普通对话 |
| `/api/chat/stream` | POST | SSE 流式对话 |
| `/api/chat/knowledge` | POST | 知识库问答 |
| `/api/chat/scenes` | GET | 获取场景列表 |
| `/api/chat/conversations` | GET | 获取对话历史列表 |
| `/api/chat/conversations/{id}/messages` | GET | 获取对话消息 |

### 5.3 冥想功能

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/meditation/session/start` | POST | 开始冥想会话 |
| `/api/meditation/session/end` | POST | 结束冥想会话 |
| `/api/meditation/mood-checkin` | POST | 情绪签到 |
| `/api/meditation/stats` | GET | 获取进度统计 |
| `/api/meditation/weekly` | GET | 获取本周进度 |

### 5.4 冥想搭子

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/teachers/list` | GET | 获取导师列表 |
| `/api/teachers/{id}` | GET | 获取导师详情 |
| `/api/teachers/select` | POST | 选择导师 |

### 5.5 其他

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/skills` | GET | 获取技能列表 |
| `/api/memory` | GET/DELETE | 记忆管理 |
| `/api/knowledge/*` | 多种 | 知识库管理 |

---

## 6. 配置说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MEDITATION_JWT_SECRET` | JWT 签名密钥 | - |
| `MEDITATION_OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `MEDITATION_DEFAULT_LLM_PROVIDER` | 默认 LLM 提供商 | `openai` |
| `MEDITATION_KNOWLEDGE_TOP_K` | 知识库检索数量 | `3` |
| `MEDITATION_CONVERSATION_MAX_TURNS` | 上下文最大轮数 | `20` |
| `DATABASE_URL` | 数据库连接 URL | SQLite 本地文件 |
| `CHROMA_DB_DIR` | ChromaDB 存储目录 | `./chroma_db` |

---

## 7. 快速启动

### 7.1 开发模式

```bash
# 克隆项目
git clone https://github.com/peace-lab-global/hush.ai.git
cd hush.ai

# 创建虚拟环境
python3 -m venv .venv && source .venv/bin/activate

# 安装依赖
pip install -e ".[meditation]"

# 复制环境变量文件
cp .env.example .env
# 编辑 .env 填入必要的 API 密钥

# 启动服务
bash scripts/start_server.sh
# 或直接运行
python -m hushai.meditation.app
```

服务启动后：

- 前台对话: http://localhost:8000
- 管理后台: http://localhost:8000/admin
- API 文档: http://localhost:8000/debug

### 7.2 生产环境 (Docker)

```bash
# 配置环境变量
export DATABASE_URL=postgresql://user:pass@host:5432/hushai
export MEDITATION_JWT_SECRET=your-secret-key

# 使用 Docker Compose
docker compose up -d
```

---

## 8. 管理后台

访问 `/admin` 进入管理后台，支持：

- **用户运营**: 用户列表、对话记录、记忆管理
- **内容运营**: 知识库导入、技能管理、场景管理
- **数据导出**: CSV/Excel 格式导出
- **管理员管理**: 多管理员账号、审计日志
- **系统设置**: LLM 参数、检索阈值

---

## 9. 开发指南

### 9.1 代码规范

```bash
# 代码格式
ruff format .

# 代码检查
ruff check .

# 运行测试
pytest

# 安全扫描
make security
```

### 9.2 添加新功能

1. **数据库模型**: 在 `db/models.py` 添加模型
2. **API 端点**: 在 `api/` 下创建路由文件
3. **业务逻辑**: 在 `core/` 下实现核心逻辑
4. **前台功能**: 在 `static/index.html` 添加前端逻辑
5. **测试覆盖**: 在 `tests/` 添加单元测试

---

## 10. 更新日志

### v0.2.0 (2026-06)

- ✨ **冥想搭子**: 支持多 AI 角色切换（小观、禅师、森林派、藏传、道家）
- ✨ **冥想追踪**: 情绪签到、进度统计、本周进度可视化
- ✨ **呼吸练习**: 4-7-8、方形呼吸、平静呼吸三种模式
- ✨ **流式对话**: SSE 实时流式输出
- ✨ **Token 刷新**: 自动续期机制
- ✨ **批量操作**: 对话、记忆、知识批量删除
- ✨ **数据导出**: CSV/Excel 格式支持
- ✨ **审计日志**: 管理员操作记录
- 🔒 **安全增强**: 危机检测、敏感词过滤
- 🔄 **LLM 降级**: 自动切换可用提供商

---

## 11. 贡献

欢迎提交 Issue 和 Pull Request：

- 提交代码前请确保通过 `pytest` 测试
- 遵循 `ruff` 代码风格规范
- 新功能模块必须具备单元测试覆盖

详细规范请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

**许可证**: [Apache License 2.0](LICENSE)
