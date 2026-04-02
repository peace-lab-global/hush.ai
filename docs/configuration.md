# 配置说明

`hush` 通过 **环境变量** 与可选的 **JSON 配置文件** 读取连接信息与行为参数。所有密钥与 URL 均只保存在本机，由 OpenAI 兼容客户端发往你配置的端点。

## 优先级规则

对每一项配置，**环境变量始终覆盖配置文件中的同名字段**（只要环境变量已设置且非空字符串）。

加载逻辑概要：

1. 解析配置文件路径（见下文「配置文件路径」）。
2. 若路径存在且为文件，则读取 JSON 对象到内存。
3. 读取各项时：**先读环境变量**，未设置时再读文件中的键。

因此推荐：**密钥用环境变量或机密管理**；模型名、超时等非敏感项可放在配置文件。

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `LLM_APPKEY` | 是* | — | OpenAI 兼容 API Key（与配置文件二选一提供） |
| `OPENAI_BASE_URL` | 否 | 官方默认 | 兼容 OpenAI Chat Completions 的网关 Base URL |
| `LLM_MODEL` | 否 | `gpt-4o-mini` | 模型名称 |
| `LLM_TIMEOUT` | 否 | `60` | 单次 HTTP 请求超时（秒），最小按实现为 1 |
| `LLM_MAX_RETRIES` | 否 | `2` | SDK 层自动重试次数，最小为 0 |
| `HUSH_CONFIG` | 否 | — | 显式指定配置文件路径；与 CLI `-c/--config` 等价（CLI 优先于本变量） |
| `HUSH_MODE` | 否 | `calm` | 对话模式，见下表；与 `hush_mode` 对应 |
| `HUSH_CALM_MODE` | 否 | — | **兼容旧版**：`1`→`calm`，`0`→`plain`；仅当 **未** 设置 `HUSH_MODE` 时读取 |

\*若通过配置文件提供 `llm_appkey`，则可不设 `LLM_APPKEY`。

### 对话模式（`HUSH_MODE` / `hush_mode`）

<a id="dialogue-modes"></a>

| 值 | 系统提示行为 | 含义 |
|----|----------------|------|
| `calm` | 哲理老人基座 + **反焦虑**后缀（默认） | 接纳情绪、语气平稳、少命令式 |
| `focus` | 基座 + **反拖延**后缀 | 小步、不羞辱、不堆清单 |
| `hype` | 基座 + **激励**后缀 | 积极有力量，避免空洞口号 |
| `plain` | **仅**哲理老人基座，无模式后缀 | 与旧版「仅禅意」一致 |
| `pua` | **独立**演练提示（不叠用哲理老人基座） | 教育向反操控：模型输出一句虚构的「施压方」台词，用于觉察练习；**非**心理咨询或危机干预 |

无效取值会在 `configure()` 时报错（进程不进入正常流程）。

#### 模式别名（仅环境变量与 JSON）

<a id="mode-aliases"></a>

`hush --mode` **只接受**上表五个规范名称。在 **`HUSH_MODE`** 或 JSON **`hush_mode`** 中可使用下列别名（由 `hushai.settings._parse_mode_strict` 解析）：

| 别名 | 解析为 |
|------|--------|
| `anti-anxiety`, `anxiety` | `calm` |
| `anti-procrastination`, `procrastination` | `focus` |
| `pump`, `energy` | `hype` |
| `none`, `zen` | `plain` |
| `anti-pua`, `antipua`, `drill` | `pua` |

#### 与 CLI 的关系

- `hush --mode MODE` 会写入当前进程的 **`HUSH_MODE`**（规范名），并**覆盖**配置文件里的 `hush_mode`（见上文优先级）。
- `--no-calm` 与 `--mode` 互斥，等价于 `--mode plain`。

## 配置文件（JSON）

### 路径如何确定

按顺序尝试：

1. **CLI**：`hush --config /path/to/config.json`（或 `-c`）— 若指定则必须存在，否则启动失败。
2. **环境变量**：`HUSH_CONFIG` 指向的路径 — 同上，必须存在。
3. **默认位置**（仅当文件已存在时自动加载；不存在则忽略，不报错）：
   - **Windows**：优先 `%APPDATA%\hush\config.json`；若未设置 `APPDATA`，实现与 Linux/macOS 类似，使用 `XDG_CONFIG_HOME` 或 `~/.config/hush/config.json`（见源码 `default_config_path()`）。
   - **Linux / macOS**：`$XDG_CONFIG_HOME/hush/config.json`，若未设置 `XDG_CONFIG_HOME` 则为 `~/.config/hush/config.json`。

### JSON 字段

根节点必须是 **JSON 对象**（`{}`），字段名与含义如下：

| 键 | 类型 | 对应环境变量 | 说明 |
|----|------|----------------|------|
| `llm_appkey` | string | `LLM_APPKEY` | API Key |
| `openai_base_url` | string | `OPENAI_BASE_URL` | 网关 Base URL |
| `llm_model` | string | `LLM_MODEL` | 模型名 |
| `llm_timeout` | number | `LLM_TIMEOUT` | 超时秒数 |
| `llm_max_retries` | integer | `LLM_MAX_RETRIES` | 重试次数 |
| `hush_mode` | string | `HUSH_MODE` | `calm` / `focus` / `hype` / `plain` / `pua`；可与上节**别名**同用 |
| `hush_calm_mode` | boolean | `HUSH_CALM_MODE` | **兼容**：`true`→`calm`，`false`→`plain`（无 `hush_mode` 时） |

示例：

```json
{
  "llm_appkey": "sk-…",
  "openai_base_url": "https://api.openai.com/v1",
  "llm_model": "gpt-4o-mini",
  "llm_timeout": 60,
  "llm_max_retries": 2,
  "hush_mode": "focus"
}
```

### 校验与错误

- JSON 语法错误、根节点非对象：进程启动失败，错误信息提示路径与解析原因。
- `--config` / `HUSH_CONFIG` 指向的路径不存在：启动失败。

## 安全提示

- 配置文件若含 `llm_appkey`，请将文件权限限制为仅本人可读（如 Unix `chmod 600`）。
- 勿将含密钥的配置提交到版本库；优先使用环境变量或 CI 密钥。
- **`pua` 模式**：提示仍会发往你所配置的 API；勿输入可识别真人或敏感隐私的细节。该功能为教育演练，不能替代专业支持；见 [SECURITY.md](../SECURITY.md)。
