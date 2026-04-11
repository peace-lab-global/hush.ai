# 文档中心

面向使用者与贡献者的说明索引。请先读仓库根目录 [README.md](../README.md)（产品定位、模式一览、速查）；下列页面按主题展开。

| 文档 | 内容 |
|------|------|
| [最小化部署](deployment-minimal.md) | **最少步骤**：venv、`MEDITATION_JWT_SECRET` + `MEDITATION_OPENAI_API_KEY`、一条 uvicorn 命令、验证 URL |
| [部署指南](deployment.md) | **分阶段完整部署**：虚拟环境、SQLite/PostgreSQL、Chroma 与 RAG、环境变量、systemd、Nginx、检查清单与常见问题 |
| [配置说明](configuration.md) | 环境变量与 JSON 字段、**五种对话模式**（含 `pua`）、**模式别名**、配置文件路径与优先级、校验错误 |
| [命令行参考](cli.md) | `hush` / `python -m hushai`、**`--mode` 与别名区别**、TTY/管道/REPL、示例、退出码、「一句话」后处理 |
| [架构概览](architecture.md) | `hushai.cli` / `settings` / `llm` / `postprocess` 职责、**系统提示如何随模式变化**（[§ 系统提示与模式](architecture.md#system-prompt-modes)）、请求流程、mermaid 流程图 |
| [开发文档](development.md) | 研发沉淀：RAG/Skills/配置管理/对话追溯的实现落点、验证方法、测试与交付清单 |

**快速链：** 五种对话模式 → [configuration.md](configuration.md#dialogue-modes)；模式别名 → [configuration.md](configuration.md#mode-aliases)；管道与 REPL → [cli.md](cli.md#no-arg-branches)。

---

# Documentation

Start with the root [README.md](../README.md). For details: **configuration** (modes, aliases, env vs file), **CLI** (flags, stdin/REPL), **architecture** (modules, `build_system_prompt`).
