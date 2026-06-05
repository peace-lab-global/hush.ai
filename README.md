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

## 1. 功能概述

`hush.ai` 是一款面向现代生活压力的智能化心理与冥想陪伴系统。它通过集成大语言模型（LLM）技术，提供两类核心产品：

- **hush CLI**: 极简禅意终端工具，支持多种心理调节模式（反焦虑、反拖延等），每次仅输出一句话，帮助用户快速决策与平复心情。
- **小观 (XiaoGuan)**: 具备长期记忆与专业知识储备的 AI 冥想老师。支持 **RAG（检索增强生成）**、**Skills（技能插件）**、**长期记忆提取** 及 **语音交互**，为用户提供个性化的深度心理陪伴。

## 2. 架构设计

系统采用模块化设计，确保高可用性与可扩展性：

- **前端层**: 提供基于 SVG 的感官交互界面，支持语音识别（ASR）与合成（TTS）。
- **API 服务层**: 基于 FastAPI 构建，负责身份认证（JWT/微信 OAuth）、对话流控制及管理接口。
- **对话引擎 (Engine)**: 核心编排层，实现多维度提示词构建、知识库检索、记忆提取与技能挂载。
- **存储层**: 
  - **关系型数据库 (PostgreSQL/SQLite)**: 存储用户信息、对话历史、结构化记忆与技能配置。
  - **向量数据库 (ChromaDB)**: 负责知识库语料与用户长期记忆的语义检索。
- **LLM 适配层**: 支持 OpenAI、DeepSeek、智谱等多种模型，支持标准 OpenAI 兼容协议。

## 3. 核心特性列表

- **RAG 知识增强**: 支持导入 Markdown 格式语料库。系统自动解析 YAML Frontmatter，进行段落感知分块与向量化，在对话中自动检索相关理论辅助回答。
- **Skills 技能插件**: 模块化技能系统，支持动态导入与挂载。智能体可自动根据配置调用技能（如：引导词生成、特定流派加持）来增强回复质量。
- **长期记忆系统**: 自动从对话中提取 7 大维度（冥想经历、情绪模式等）的记忆，支持 0~1 重要性评分与自动归档。
- **动态配置管理**: 提供完善的管理后台，支持 LLM 参数、检索阈值、API Key 等运行参数的 **动态调整与立即生效**。
- **完整对话追溯**: 运行时环境中客户与智能体之间的所有对话记录均被完整保存，支持多维度查询与回溯分析。
- **安全与合规**: 内置危机信号检测护栏，识别敏感词并自动提供专业求助建议。

## 4. 使用示例

### hush CLI 示例
```bash
# 单次禅意提问
hush "现在心跳很快，怎么办？"
# -> 深吸一口气，感受空气在鼻尖的凉意。
```

### 冥想老师 API 示例
```bash
# 调用对话接口（自动挂载技能与检索知识库）
curl -X POST http://localhost:8000/api/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "我最近压力很大", "skill_ids": ["relax-guide-01"]}'
```

## 5. 配置说明

所有核心配置均支持通过环境变量（`.env`）或管理后台动态设置：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `MEDITATION_JWT_SECRET` | 认证签名密钥 | `your-secret-key` |
| `MEDITATION_OPENAI_API_KEY` | LLM API 密钥 | `sk-...` |
| `MEDITATION_DEFAULT_LLM_PROVIDER` | 默认模型提供商 | `openai` / `deepseek` / `zhipu` |
| `MEDITATION_KNOWLEDGE_TOP_K` | 知识库检索数量 | `3` |
| `MEDITATION_CONVERSATION_MAX_TURNS` | 上下文最大轮数 | `20` |

## 6. 部署指南

### 快速启动 (SQLite 模式)
```bash
git clone https://github.com/peace-lab-global/hush.ai.git
cd hush.ai
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[meditation]"
# 启动服务
bash scripts/start_server.sh
```

### 生产环境部署 (Docker)
```bash
docker compose up -d
# 配置环境变量后启动应用镜像
```

## 7. 贡献规范

我们欢迎任何形式的贡献：
- **提交 Issue**: 报告 Bug 或提出新功能建议。
- **Pull Request**: 提交代码前请确保通过 `pytest` 测试。
- **代码风格**: 遵循 `ruff` 配置的格式要求。
- **测试覆盖**: 新功能模块必须具备单元测试覆盖。

更多细节请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。

---
**许可证**: [Apache License 2.0](LICENSE)
