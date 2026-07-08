---
kind: configuration_system
name: 配置系统：双轨加载（CLI JSON + 服务 .env）与环境变量覆盖
category: configuration_system
scope:
    - '**'
source_files:
    - hushai/settings.py
    - hushai/meditation/config.py
    - hushai/cli.py
    - hushai/meditation/app.py
    - .env.example
---

## 体系概览

本仓库采用**两套并行的配置子系统**，分别服务于 CLI 与 FastAPI 冥想服务，统一遵循“环境变量优先于配置文件”的原则。

- **CLI 配置（`hushai/settings.py`）**：通过 `configure()` 在进程入口一次性解析 JSON 配置文件，随后所有 `get_*` 函数按“环境变量 > JSON 文件 > 默认值”的优先级读取。
- **服务配置（`hushai/meditation/config.py`）**：使用 `MeditationConfig` dataclass 描述全部运行时参数，启动时从 `.env` 加载并通过全局单例 `get_config()` 暴露给应用各层。

两套系统互不依赖，由各自入口负责初始化。

## 关键文件与包

- `hushai/settings.py` — CLI 配置解析器，支持 JSON 配置文件、模式别名、布尔/数值容错转换、测试重置。
- `hushai/meditation/config.py` — 冥想服务配置模型，基于 dataclass + 类方法 `from_env()` 映射 `MEDITATION_*` 环境变量。
- `hushai/cli.py` — `hush` CLI 入口，调用 `configure(args.config)` 完成配置加载，并将 `--mode` 写入 `HUSH_MODE` 环境。
- `hushai/meditation/app.py` — FastAPI 应用工厂，通过 `get_config()` 注入 host/port/debug/CORS 等运行时参数。
- `.env.example` — 开发用环境变量模板，列出所有 `MEDITATION_*` 键及注释说明。
- `pyproject.toml` — 通过 `[project.scripts]` 注册 `hush` / `hush-meditation` / `hush-init-knowledge` 三个可执行入口。

## 架构与约定

### 1. CLI 配置（JSON + 环境变量）

- 配置文件路径解析顺序：`--config PATH` → `HUSH_CONFIG` 环境变量 → 平台默认路径（Linux/macOS `~/.config/hush/config.json`，Windows `%APPDATA%\hush\config.json`）。
- 显式传入的路径不存在会抛出 `RuntimeError`；未找到文件则使用空字典。
- 每个配置项提供独立的 `get_xxx()` 函数，内部实现“读 env → 读 JSON → 回退默认值”的三段式逻辑。
- 模式字段 `hush_mode` / `HUSH_MODE` 支持别名映射（如 `anti-anxiety` → `calm`），非法值在 `configure()` 阶段即报错。
- 提供 `reset_for_tests()` 供 pytest 清理模块级缓存 `_CONFIG_DATA`。

### 2. 服务配置（dataclass + .env）

- 模块导入时自动尝试加载项目根目录下的 `.env`（`dotenv.load_dotenv(override=True)`）。
- `MeditationConfig.from_env()` 通过显式 `mapping` 将 `MEDITATION_*` 环境变量映射到 dataclass 字段，并做类型转换（bool/int/str）。
- 全局 `_config` 单例 + `get_config()` / `set_config()` / `reset_config()` 三件套，便于单元测试替换配置。
- 所有敏感字段（JWT secret、LLM API key、微信支付证书路径等）均作为可选字符串，留空表示未配置。

### 3. 启动流程

- CLI：`main()` → 处理 `--mode` 写入 `HUSH_MODE` → `configure(path)` → 业务逻辑。
- 服务：`uvicorn.run("hushai.meditation.app:get_app")` → `create_app()` → `get_config()` 读取 host/port/debug/CORS → 挂载路由与静态文件。

## 开发者应遵循的规则

1. **新增配置项**
   - CLI：在 `settings.py` 中新增 `get_xxx()` 函数，并在 `configure()` 之前确保能解析新字段。
   - 服务：在 `MeditationConfig` dataclass 中添加字段，并在 `from_env()` 的 `mapping` 中注册 `MEDITATION_XXX` 环境变量映射。

2. **环境变量命名规范**
   - 服务侧统一以 `MEDITATION_` 前缀区分，避免与 CLI 或第三方库冲突。
   - 布尔值接受 `1/true/yes/on` 为真，其余为假；整型解析失败时静默跳过。

3. **配置文件格式**
   - CLI 仅支持顶层 JSON 对象，不支持嵌套结构；如需分组请在键名中使用下划线分隔（如 `llm_timeout`）。

4. **测试隔离**
   - 使用 `settings.reset_for_tests()` 清空 CLI 配置缓存。
   - 使用 `meditation.config.set_config(MeditationConfig(...))` 注入内存配置，或用 `reset_config()` 恢复。

5. **安全注意事项**
   - JWT secret、LLM API Key、微信支付证书路径等敏感字段不应硬编码，必须通过环境变量或受保护的配置文件注入。
   - 生产环境务必设置 `MEDITATION_DEBUG=false` 以关闭 CORS 通配符与调试端点。

6. **向后兼容**
   - `get_mode()` 仍兼容旧版 `HUSH_CALM_MODE` / `hush_calm_mode` 布尔开关，迁移到新 `HUSH_MODE` 后无需立即删除。
