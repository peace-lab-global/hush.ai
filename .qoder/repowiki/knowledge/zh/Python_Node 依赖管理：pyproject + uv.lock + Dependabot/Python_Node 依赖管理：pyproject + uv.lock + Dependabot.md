---
kind: dependency_management
name: Python/Node 依赖管理：pyproject + uv.lock + Dependabot
category: dependency_management
scope:
    - '**'
source_files:
    - pyproject.toml
    - uv.lock
    - .github/dependabot.yml
    - Makefile
    - scripts/start_server.sh
---

## 1. 使用的系统与方法
- Python 包声明与可选依赖：`pyproject.toml`（PEP 621），使用 `setuptools` 作为构建后端，通过 `[project.optional-dependencies]` 划分 `dev`、`meditation` 等可选集合。
- 锁定文件：`uv.lock`（由 uv 生成），记录所有解析出的精确版本与哈希，支持多平台 marker 分派；同时存在 `.venv` / `.venv-pip` 两个虚拟环境目录用于本地开发。
- Node.js：根目录有空的 `package.json` 与 `package-lock.json`，当前未引入前端依赖，仅占位。
- 自动化更新：`.github/dependabot.yml` 配置了 pip 与 github-actions 的每周自动 PR。
- 构建与安装入口：`Makefile` 提供 `install`、`dev`、`build` 等目标，统一调用 `pip install -e .[dev]` 和 `build/twine`。

## 2. 关键文件与位置
- `pyproject.toml` — 包元数据、运行时依赖、可选依赖、脚本入口、工具配置（pytest/ruff/mypy）
- `uv.lock` — 完整锁定的 Python 依赖树（含多平台 resolution markers）
- `.github/dependabot.yml` — 依赖更新策略（pip、github-actions）
- `Makefile` — 安装、格式化、类型检查、测试、安全扫描、打包的统一入口
- `scripts/start_server.sh` — 生产启动时通过 venv 中的 uvicorn 运行 FastAPI 应用
- `hushai/__init__.py`（动态版本读取）— 配合 `tool.setuptools.dynamic.version` 从源码读取版本号

## 3. 架构与约定
- 单一顶层包 `hushai`，通过 `packages = ["hushai"]` 发布；CLI 与 FastAPI 服务均以 entry points 暴露（`hush`、`hush-meditation`、`hush-init-knowledge`）。
- 依赖分层：核心运行时仅声明 `openai>=1.0.0`；FastAPI 相关依赖放入 `meditation` 可选组，避免最小化安装体积。
- 版本约束风格：全部使用 `>=X.Y.Z` 宽松下限，不固定上限，将稳定性交由 `uv.lock` 保证。
- 多 Python 版本兼容：`requires-python = ">=3.9"`，并在 `uv.lock` 中按 `python_full_version` 与 `sys_platform` 标记分发不同轮子。
- 无私有源或 vendoring：所有包来源均为 PyPI（`source.registry = https://pypi.org/simple`），未发现 `setup.cfg`、`requirements.txt`、`poetry.lock`、`Pipfile` 或 vendor 目录。

## 4. 开发者应遵循的规则
- 新增依赖一律在 `pyproject.toml` 对应分组下声明，优先放入 `optional-dependencies` 而非 `dependencies`。
- 修改依赖后使用 `uv lock` 重新生成 `uv.lock`，并提交锁文件，确保 CI 可复现。
- 不要手动编辑 `uv.lock`；如需调整范围，只改 `pyproject.toml` 并重新锁定。
- 使用 Makefile 目标进行日常操作：`make dev` 安装开发依赖，`make test` 运行带覆盖率断言的测试，`make security` 执行 bandit 扫描。
- 前端依赖暂不引入；若后续需要，应在 `package.json` 中正式声明并通过 npm/yarn/pnpm 锁定，再同步更新 Dependabot 配置。
- 保持 `openai` 为唯一强制运行时依赖，其余功能按需以可选组形式扩展。