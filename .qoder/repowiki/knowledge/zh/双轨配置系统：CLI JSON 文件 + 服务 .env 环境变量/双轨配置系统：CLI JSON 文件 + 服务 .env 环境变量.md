---
kind: configuration_system
name: 双轨配置系统：CLI JSON 文件 + 服务 .env 环境变量
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

## 系统概览

hush.ai 采用两套并行的配置体系，分别服务于 CLI 工具与 FastAPI 服务进程，统一遵循「环境变量优先于配置文件」的原则。

### 1. CLI 配置（hushai/settings.py）

- 配置文件格式：JSON，默认路径 ~/.config/hush/config.json（Linux/macOS）或 %APPDATA%\hush\config.json（Windows），可通过 HUSH_CONFIG 环境变量或 --config 参数覆盖。
- 加载流程：configure(cli_config) 在进程入口调用一次，解析并缓存到全局 _CONFIG_DATA；支持 reset_for_tests() 用于测试隔离。
- 优先级规则：环境变量 > JSON 文件 > 旧版兼容键 > 内置默认值。例如 get_mode() 依次检查 HUSH_MODE → hush_mode → HUSH_CALM_MODE/hush_calm_mode → 默认 calm。
- 受管配置项：LLM_APPKEY、OPENAI_BASE_URL、HUSH_MODE（calm/focus/hype/plain/pua，含别名映射）、LLM_MODEL（默认 gpt-4o-mini）、LLM_TIMEOUT（默认 60）、LLM_MAX_RETRIES（默认 2）。

### 2. 冥想服务配置（hushai/meditation/config.py）

- 配置文件来源：项目根目录 .env 文件，通过 python-dotenv 在模块导入时自动加载（override=True）。
- 数据结构：MeditationConfig dataclass（frozen），所有字段带默认值，通过 from_env() 从 os.environ 按命名映射填充。
- 命名约定：所有环境变量以 MEDITATION_ 前缀，字段名去前缀后对应 dataclass 属性。例如 MEDITATION_OPENAI_API_KEY → openai_api_key。
- 受管配置项：数据库（POSTGRES_URL、CHROMA_DIR）、认证（JWT_SECRET/ALGORITHM/EXPIRE_MINUTES）、微信小程序（WX_APPID/SECRET/支付相关）、LLM 提供商（DEFAULT_LLM_PROVIDER + 各厂商 *_API_KEY/*_BASE_URL/*_MODEL）、Embedding、业务参数（MEMORY_TOP_K/KNOWLEDGE_TOP_K/CONVERSATION_MAX_TURNS）、服务（HOST/PORT/DEBUG/CORS_ORIGINS）、安全（ENCRYPTION_KEY）。

### 3. 启动集成点

- CLI 入口：hushai/cli.py::main() 先处理 --mode/--no-calm 参数写入 HUSH_MODE，再调用 settings.configure(args.config)。
- FastAPI 入口：hushai/meditation/app.py::run() 通过 get_config() 获取 MeditationConfig，注入到 Uvicorn 的 host/port/reload 及 CORS 中间件。

### 4. 设计决策与约束

- 无集中配置框架：未使用 pydantic-settings、dynaconf、omegaconf 等第三方库，纯手写解析逻辑，保持零依赖。
- 类型安全：服务侧用 frozen dataclass 提供强类型访问；CLI 侧返回 str | None，由调用方处理缺失场景。
- 向后兼容：CLI 保留对旧布尔开关 HUSH_CALM_MODE/hush_calm_mode 的兼容解析。
- 测试友好：两处均暴露 reset 函数（settings.reset_for_tests()、config.reset_config()）供 pytest 清理状态。
- 密钥管理：敏感信息仅通过环境变量注入，不硬编码；.env.example 提供完整模板。

## 开发者规范

1. 新增配置项：CLI 侧在 hushai/settings.py 添加 getter，遵循「环境变量名大写蛇形 + JSON 键小写下划线」命名约定；服务侧在 MeditationConfig dataclass 增加字段，并在 from_env() 的 mapping 字典中注册。
2. 不要直接读 os.environ：应通过 get_config() 或 settings.get_*() 访问，确保默认值和类型转换一致。
3. 生产环境禁用 debug：MEDITATION_DEBUG=true 会放宽 CORS 为 ["*"] 且开启 uvicorn reload。
4. 密钥轮换：修改 MEDITATION_JWT_SECRET 或 MEDITATION_ENCRYPTION_KEY 后需重启服务，数据不会自动重新加密。
5. 配置文件校验：CLI 的 JSON 配置必须为顶层对象（dict），否则抛出 RuntimeError；建议配合 pyproject.toml 中的 schema 验证脚本。

## 关键文件

- hushai/settings.py — CLI 配置解析（JSON + 环境变量）
- hushai/meditation/config.py — 服务配置 dataclass + .env 加载
- hushai/cli.py — CLI 入口，触发 configure()
- hushai/meditation/app.py — FastAPI 应用，消费 MeditationConfig
- .env.example — 完整环境变量模板
- tests/test_settings.py — 配置单元测试