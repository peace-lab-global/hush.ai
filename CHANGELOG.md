# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-04

### Added

- **冥想搭子（多 AI 角色切换）**：5 个内置导师（小观/禅师/森林派/藏传/道家），独立 system prompt 与音色。
- **冥想追踪**：情绪签到（1-10 分）、进度统计、本周可视化、连续天数。
- **呼吸练习**：4-7-8、方形呼吸、平静呼吸三种引导。
- **流式对话（SSE）**：`/api/chat/stream` 实时流式输出。
- **Token 刷新机制**：access + refresh 双 token。
- **批量操作**：对话/记忆/知识批量删除。
- **数据导出**：CSV / Excel 格式。
- **审计日志**：管理员操作记录。
- **危机检测 & 敏感词过滤**：自动识别并提供求助建议。
- **LLM 自动降级**：多提供商（OpenAI / DeepSeek / 智谱 / Kimi）按可用性切换。
- **RAG 知识库**：Markdown + YAML frontmatter 语料导入、ChromaDB 段落感知分块与向量检索。
- **技能插件系统**：动态导入、批量挂载、按配置触发。
- **长期记忆**：从对话中自动提取 7 维度记忆（冥想经历、情绪模式、目标进展等）。
- **管理后台**：用户运营、内容运营、审计、CSV/Excel 导出、LLM 参数配置、远程知识源管理。
- **微信小程序登录** + **Native / JSAPI 微信支付 v3** + 回调验签/解析。
- **咨询台（Counseling）**：咨询师面板、预约、知情同意、合同、钱包、抽佣。
- **远程知识源适配器**：URL / Coze / IMA 三类源的文档列表与导入。
- **加密工具**：`core/encryption.py` 字段级加密辅助。
- **测试覆盖**：294 个测试（新增 37 个），`wechat_pay` 0% → 90%，`remote_knowledge` 0% → 57%，`admin/audit` 0% → 100%，项目总覆盖率 78%。
- **Release 工作流**：推送 `v*` tag 自动构建 sdist/wheel 并发布到 GitHub Release。
- **CI 矩阵**：Python 3.9~3.13 + Windows/macOS 烟测。

### Changed

- **README 全面升级**：中心 logo、价值主张、ASCII 架构图、API 表、快速启动、FAQ、文档链接。
- **文档结构化**：`docs/` 拆分为 architecture / cli / configuration / deployment / development 等专题。
- **`.gitignore` 完整化**：覆盖 `.coverage *`、`.DS_Store`、`*.db`、macOS 残留、Chromadb 数据等。
- **CHANGELOG 引入 Keep a Changelog 规范**。

### Removed

- 移除被错误追踪的 `.DS_Store` / `.coverage 2` / `meditation_local.db`（`.gitignore` 规则之前未生效），本地构建产物不再入库。

## [0.1.0] - 2025-08-29

### Added

- 初始提交：基础 `hush` CLI 框架、OpenAI 兼容 chat、`LLM_APPKEY` 配置、单句回复、REPL 模式。
- 项目基础设施：Apache-2.0 + NOTICE、Code of Conduct、安全/贡献/治理文档。
- CI：lint、type-check、tests、coverage gate、sdist/wheel build。
- Dependabot、issue/PR 模板、pre-commit 配置、`Makefile` 目标、`py.typed`。
- 可靠性：`LLM_TIMEOUT` / `LLM_MAX_RETRIES`，OpenAI SDK 错误映射为中文提示。
- 配置：JSON 配置文件（`--config` / `HUSH_CONFIG` / XDG 路径）、env 覆盖文件。
- CLI：stdin pipe 模式、`--json-errors`。
- CI：Python 3.13 加入矩阵；Windows/macOS 烟测。
- Release：GitHub Release workflow on `v*` tags。
- 文档：所有 user-facing docs 同步 `pua` 模式（`docs/configuration.md`、`docs/cli.md`、`docs/architecture.md`、README）。

[Unreleased]: https://github.com/peace-lab-global/hush.ai/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/peace-lab-global/hush.ai/releases/tag/v0.2.0
[0.1.0]: https://github.com/peace-lab-global/hush.ai/releases/tag/v0.1.0

