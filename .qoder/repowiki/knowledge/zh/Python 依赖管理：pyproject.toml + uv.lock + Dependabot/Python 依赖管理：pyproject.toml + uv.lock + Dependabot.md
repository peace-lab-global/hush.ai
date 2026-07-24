---
kind: dependency_management
name: Python 依赖管理：pyproject.toml + uv.lock + Dependabot
category: dependency_management
scope:
    - '**'
source_files:
    - pyproject.toml
    - uv.lock
    - .github/dependabot.yml
    - Makefile
---

## 1. 使用的系统与工具链
- **包声明**：`pyproject.toml`（PEP 621），使用 `setuptools.build_meta` 作为构建后端。
- **锁定文件**：`uv.lock`，由 [uv](https://github.com/astral-sh/uv) 生成并维护，记录所有解析出的依赖及其哈希值，支持多 Python 版本与平台的 resolution-markers。
- **虚拟环境**：`.venv/`、`.venv-pip/` 两个 venv 并存，分别对应 uv 与 pip 工作流；项目根目录未提交 lock 之外的 vendored 第三方代码。
- **更新自动化**：GitHub Dependabot 配置在 `.github/dependabot.yml`，每周扫描 `pip` 与 `github-actions` 生态，最多保留 10 个 PR。
- **可选依赖组**：通过 `[project.optional-dependencies]` 将运行时与开发依赖解耦，提供 `dev`、`meditation` 两组 extras。
- **构建/发布**：Makefile 封装 `build`、`twine check` 等流程，配合 `hushai.egg-info` 元数据完成分发。

## 2. 关键文件与位置
- `pyproject.toml` — 项目元数据、依赖声明、可选依赖组、脚本入口、tool 配置（pytest/ruff/mypy）
- `uv.lock` — 完整依赖树锁定快照（含多平台 wheel/sdist 哈希）
- `.github/dependabot.yml` — 自动升级策略
- `Makefile` — 安装、测试、安全扫描、构建的便捷命令
- `.pre-commit-config.yaml` — 提交前钩子（lint/typecheck/test 联动）
- `docker-compose.yml` / `Dockerfile*`（如有）— 容器化时的依赖复现（当前仓库未见 Dockerfile，但 compose 存在）

## 3. 架构与约定
- **单一真相源**：`pyproject.toml` 是依赖声明的唯一来源，`uv.lock` 是其确定性快照；二者均纳入版本控制。
- **可选依赖分组**：核心 CLI 仅依赖 `openai>=1.0.0`；FastAPI 服务相关依赖放入 `meditation` extra，避免最小安装体积膨胀。
- **多 Python 版本兼容**：`requires-python = ">=3.9"`，lock 文件中为不同 Python 版本/平台分别记录 resolved 包，确保跨环境可重现。
- **安全与质量内建**：`dev` extra 包含 `bandit`、`pip-audit`、`ruff`、`mypy`、`pytest-cov`，并通过 Makefile 统一调用。
- **无私有注册表/供应商目录**：未发现 `setup.cfg`、`requirements.txt`、`poetry.lock`、`Pipfile`、`vendor/` 或自定义 PyPI 镜像配置，全部走官方 pypi.org/simple。

## 4. 开发者应遵循的规则
1. **新增依赖只改 `pyproject.toml`**，然后运行 `uv lock` 同步 `uv.lock`，不要手动编辑锁文件。
2. **区分 core 与 optional**：公共库放 `dependencies`，仅 FastAPI 服务需要的库放入 `meditation` extra，保持最小安装面。
3. **不提交本地 venv**：`.venv/`、`.venv-pip/` 已在 `.gitignore`，协作时以 `uv sync` 或 `pip install -e .[dev]` 重建。
4. **接受 Dependabot PR**：每周自动生成的 pip/github-actions 升级 PR 应定期 review 合并，保持依赖新鲜。
5. **构建前执行检查**：`make check` 会依次运行 ruff format --check、mypy、pytest，确保依赖变更不会破坏类型/测试契约。
6. **发布前校验**：`make build` 会调用 `build` + `twine check`，确认打包产物与依赖声明一致。