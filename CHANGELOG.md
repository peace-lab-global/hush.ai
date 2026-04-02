# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation

- Synced all user-facing docs for **`pua` 模式**：`docs/configuration.md`（五种模式表、**完整别名表**、CLI 与 env 差异）、`docs/cli.md`（`--mode` 说明与示例）、`docs/architecture.md`（**系统提示与模式**小节）、`docs/README.md`（索引与锚点）、`SECURITY.md`（演练边界与隐私提示）；README 已含模式表与 FAQ。
- Added [docs/](docs/README.md): configuration reference, CLI reference, architecture (with module table and flowchart).
- Refreshed [README.md](README.md) (TOC, quick start, FAQ, links to docs).
- README: centered hero, expanded badges, value proposition, demo blocks, `<details>` FAQ, fuller English mirror.
- Expanded [CONTRIBUTING.md](CONTRIBUTING.md) (repo layout, CI matrix, tooling commands).
- Expanded [SECURITY.md](SECURITY.md) (data handling, `python -m pip_audit`).
- Refined [GOVERNANCE.md](GOVERNANCE.md) and [MAINTAINERS.md](MAINTAINERS.md) (docs pointer).

### Added

- **`pua` 模式（反PUA 演练）**：教育向一句台词模拟，独立系统提示；别名 `anti-pua` / `antipua` / `drill`。
- **多模式切换**：`calm`（反焦虑）、`focus`（反拖延）、`hype`（激励）、`plain`（仅基础提示）。`HUSH_MODE`、`hush_mode`（JSON）、`--mode`；兼容 `HUSH_CALM_MODE` / `hush_calm_mode` 与 `--no-calm`（→`plain`）。
- Initial `hush` CLI: OpenAI-compatible chat via `LLM_APPKEY`, one-sentence replies, REPL mode.
- Project hygiene: Apache-2.0 + `NOTICE`, Code of Conduct, security/contributing/governance docs.
- CI (lint, type-check, tests, coverage gate, sdist/wheel build), Dependabot, issue/PR templates.
- Dev tooling: Ruff, Mypy, pytest-cov, pre-commit config, `Makefile` targets, `py.typed`.
- **Reliability:** `LLM_TIMEOUT` / `LLM_MAX_RETRIES`; OpenAI SDK errors mapped to concise Chinese messages.
- **Configuration:** JSON config file (`--config` / `HUSH_CONFIG` / default XDG-style path); env overrides file.
- **CLI:** stdin pipe mode when not a TTY; `--json-errors` for machine-readable stderr.
- **CI:** Python 3.13 in matrix; Windows/macOS smoke tests.
- **Release:** GitHub Release workflow on `v*` tags (attach sdist/wheel).

