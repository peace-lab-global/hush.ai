---
kind: build_system
name: Python 包构建与 CI/CD 流水线
category: build_system
scope:
    - '**'
source_files:
    - pyproject.toml
    - Makefile
    - .github/workflows/ci.yml
    - .github/workflows/release.yml
    - docker-compose.yml
    - .pre-commit-config.yaml
---

## 构建系统概览

hush.ai 采用现代 Python 打包标准（PEP 517/621），以 pyproject.toml 为单一事实来源，配合 Makefile、GitHub Actions 和 docker-compose 形成从本地开发到容器化部署的完整流水线。

### 核心工具链

- 构建后端：setuptools（setuptools.build_meta），通过 [tool.setuptools] 声明包名与动态版本读取自 hushai.__version__
- 依赖管理：pyproject.toml 中定义可选依赖组 dev、meditation，并通过 dependency-groups.dev 提供 uv 兼容分组
- 入口点：三个 CLI 命令通过 [project.scripts] 注册：hush、hush-meditation、hush-init-knowledge
- 代码质量：Ruff（lint + format）、Mypy（类型检查）、Bandit（安全扫描）
- 测试：pytest + pytest-cov，覆盖率阈值 70%

### 本地开发工作流

make install 安装基础包
make dev 安装开发依赖（含 meditation 子功能）
make check 运行 lint + format --check + typecheck + test
make build 生成 sdist/wheel 并 twine check

Makefile 将常用任务抽象为单字母目标，避免开发者直接记忆 pip/pytest/ruff 参数。

### CI 流水线（GitHub Actions）

.github/workflows/ci.yml 在每次 push/PR 时并行执行：

1. Lint & Test Matrix：在 Python 3.9–3.13 五版本上运行 ruff check/format、mypy、bandit、pytest（带覆盖率 XML 输出）
2. Smoke 跨平台：在 windows-latest、macos-latest 上快速验证基本可导入性
3. Build sdist/wheel：独立 job 构建分发包并用 twine check 校验元数据

.github/workflows/release.yml 监听 v* 标签推送，自动构建并发布 GitHub Release 附件。

### 依赖隔离与可选功能

- 核心包仅依赖 openai>=1.0.0，保持最小运行时
- meditation 可选组包含 FastAPI、SQLAlchemy、ChromaDB、Alembic 等 Web/数据库相关依赖
- 开发环境通过 pip install -e ".[dev]" 一次性安装所有开发工具

### 容器化编排

docker-compose.yml 提供两个外部服务：
- PostgreSQL 16 Alpine：端口 5432，健康检查使用 pg_isready
- ChromaDB：向量数据库，端口 8001，持久化卷挂载

应用本身未提供 Dockerfile，推测通过 hush-meditation 命令在宿主机或上游编排器中启动。

### 预提交钩子

.pre-commit-config.yaml 在 git commit 前自动执行：
- 通用钩子：尾随空白、文件结尾、YAML/JSON 校验、大文件检测（>500KB）、禁止直推 main/master
- Ruff：自动修复 + 格式化

### 版本策略

版本号通过 dynamic = ["version"] 从 hushai.__version__ 属性读取，发布流程基于 Git tag（v*）触发 release workflow。

## 开发者约定

1. 新增依赖必须写入 pyproject.toml 对应分组，不要单独维护 requirements.txt
2. 新功能需补充 pytest 用例，确保覆盖率不低于 70%
3. 提交前运行 make check，CI 会拒绝格式不规范或缺少类型注解的代码
4. 发布新版本需打 vX.Y.Z 标签，release workflow 会自动构建并发布二进制
5. 本地调试 meditation 服务时，先 docker compose up -d 启动 PostgreSQL 与 ChromaDB 依赖