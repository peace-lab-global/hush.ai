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
[![GitHub stars](https://img.shields.io/github/stars/peace-lab-global/hush.ai?style=social)](https://github.com/peace-lab-global/hush.ai)
[![Issues](https://img.shields.io/github/issues/peace-lab-global/hush.ai)](https://github.com/peace-lab-global/hush.ai/issues)

[文档](#文档) · [安装](#安装) · [演示](#演示) · [配置](#配置) · [贡献](#贡献)

</div>

---

## 它是什么

`hush` 是一个运行在终端里的 **禅意 AI CLI**：只需配置 **`LLM_APPKEY`**（OpenAI 兼容 API），默认以「哲理老人」的口吻回答；并在本地把模型输出 **压成一句话**（句末标点切首句，否则取首行并截断），避免长篇大论。（**例外**：`pua` 模式使用独立演练提示，不叠用哲理老人基座，见下表与 [配置说明](docs/configuration.md)。）

内置多种 **对话模式**（默认 `calm`）：多数模式在系统提示中追加不同取向的约束并匹配 **REPL 欢迎语**；`pua` 为教育向反操控演练。

| 模式 | 含义 |
|------|------|
| `calm` | **反焦虑**：接纳情绪、语气平稳、少命令式（默认） |
| `focus` | **反拖延**：小步行动、不羞辱、不堆清单 |
| `hype` | **打鸡血**：积极有力量，避免空洞口号 |
| `plain` | 仅保留基础「哲理老人」提示，不追加模式后缀 |
| `pua` | **反PUA 演练**：模型扮演对话里「施压一方」可能说出的一句台词（教育向、虚构情境），便于练习觉察与回应边界；**非**心理咨询，遇真实风险请寻求专业帮助 |

切换：`--mode calm|focus|hype|plain|pua`，或环境变量 `HUSH_MODE`，或 JSON `hush_mode`。**别名**（仅 env / JSON，如 `anti-pua`→`pua`）见 [docs/configuration.md · 模式别名](docs/configuration.md#mode-aliases)。兼容旧版：`HUSH_CALM_MODE=0` / `hush_calm_mode: false` 等价于 `plain`；`--no-calm` 等价于 `--mode plain`。

适合：想要 **极简回答**、在脚本/管道里嵌入一句点拨、或在 REPL 里慢问慢答的你。

---

## 为什么选择 hush

|  |  |
|--|--|
| **一句到底** | 客户端强制单句输出，适合「点一下就走」的决策场景。 |
| **多模式** | calm / focus / hype / plain / pua，一键切换语气取向（见上表）。 |
| **终端原生** | 单次 / 管道 / 交互三种模式；`--json-errors` 方便自动化。 |
| **可配置、可观测** | 超时与重试、中文错误映射；JSON 配置 + 环境变量覆盖。 |
| **工程化** | Apache-2.0、CI（多版本 Python + 跨平台烟测）、类型与测试覆盖门槛。 |

---

## 文档

| 文档 | 说明 |
|------|------|
| [docs/README.md](docs/README.md) | 文档中心入口 |
| [docs/configuration.md](docs/configuration.md) | 环境变量、JSON 配置、路径与优先级 |
| [docs/cli.md](docs/cli.md) | 参数、管道、REPL、退出码 |
| [docs/architecture.md](docs/architecture.md) | 模块职责与请求流程 |

---

## 目录

- [它是什么](#它是什么)
- [为什么选择 hush](#为什么选择-hush)
- [文档](#文档)
- [安装](#安装)
- [演示](#演示)
- [配置](#配置)
- [LLM 接入说明](#llm-接入说明)
- [使用速查](#使用速查)
- [常见问题](#常见问题)
- [贡献](#贡献)
- [社区、安全与许可证](#社区安全与许可证)
- [English](#english)

---

## 安装

**环境：** Python **3.9+**

**从源码安装（推荐）：**

```bash
git clone https://github.com/peace-lab-global/hush.ai.git
cd hush.ai
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python3 -m pip install -U pip
python3 -m pip install -e .
```

验证：

```bash
hush --version
# 或
python3 -m hushai --version
```

> **PyPI：** 若已发布 wheel，可使用 `pip install hushai`（以 [CHANGELOG](CHANGELOG.md) 与 [MAINTAINERS](MAINTAINERS.md) 为准）；当前默认以源码安装说明为主。

---

## 演示

**单次提问（输出为一句）：**

```bash
export LLM_APPKEY='你的_API_Key'
hush "心很乱的时候，先做哪一件事？"
```

终端可能类似：

```text
$ hush "心很乱的时候，先做哪一件事？"
先停三息，再决定下一步。
```

**管道：**

```bash
echo "今天最重要的是什么？" | hush
```

**交互：**

```bash
hush
# 提示符 > 下输入问题；exit / quit / q 退出
```

**反 PUA 演练（`pua`）：**

```bash
hush --mode pua "领导开会时当众说我太敏感，换一句他可能说的话"
```

---

## 配置

**原则：** 同一键 **环境变量优先于配置文件**（详见 [docs/configuration.md](docs/configuration.md)）。

### LLM 接入说明

`hush` 使用 **OpenAI 官方 Python SDK** 调用 **`chat.completions.create`**，因此需要支持 **OpenAI 兼容** 的 Chat Completions 端点（多数云厂商、自建网关会提供兼容 Base URL 与模型名，具体以服务商文档为准）。

**最小配置（使用 OpenAI 官方 API 时）：** 只需 API Key；未设置 `OPENAI_BASE_URL` 时，SDK 使用官方默认地址；未设置 `LLM_MODEL` 时默认为 `gpt-4o-mini`。

```bash
export LLM_APPKEY='你的_API_Key'   # 勿提交到 git，勿贴在公开处
hush "你好"
```

**自建网关或其它云（示例思路，非唯一写法）：** 在服务商控制台创建兼容 OpenAI 的 Key，并抄下 **Base URL** 与 **模型 ID**，再写入环境变量或 JSON：

```bash
export LLM_APPKEY='…'
export OPENAI_BASE_URL='https://你的兼容网关/v1'   # 末尾是否带 /v1 以厂商说明为准
export LLM_MODEL='模型名或 deployment 名'
hush "你好"
```

**用 JSON 文件代替部分环境变量（推荐把 Key 只放在本机文件 + 权限收紧）：**

```json
{
  "llm_appkey": "…",
  "openai_base_url": "https://…",
  "llm_model": "…"
}
```

配合 `hush --config /path/to/config.json` 或默认路径下的 `config.json`；**环境变量仍会覆盖**文件中同名字段。

**安全：** 密钥等同于账号能力，勿写入仓库；可参考 [SECURITY.md](SECURITY.md)。

### 常用环境变量

| 变量 | 说明 |
|------|------|
| `LLM_APPKEY` | API Key（可与文件中的 `llm_appkey` 二选一） |
| `OPENAI_BASE_URL` | 兼容网关 Base URL；**不设**则走 OpenAI 官方默认端点 |
| `LLM_MODEL` | 模型名，默认 `gpt-4o-mini` |
| `LLM_TIMEOUT` | 超时（秒），默认 `60` |
| `LLM_MAX_RETRIES` | SDK 重试次数，默认 `2` |
| `HUSH_CONFIG` | 配置文件路径（与 `--config` 二选一；**命令行优先**） |
| `HUSH_MODE` | `calm` / `focus` / `hype` / `plain` / `pua`；优先级高于文件中的 `hush_mode` |
| `HUSH_CALM_MODE` | （兼容）`1` 等价于 `calm`，`0` 等价于 `plain`，仅当未设置 `HUSH_MODE` 时生效 |

### 配置文件（JSON）

默认路径（文件**存在**时才自动加载）：

- Linux / macOS：`~/.config/hush/config.json`（或 `$XDG_CONFIG_HOME/hush/config.json`）
- Windows：`%APPDATA%\hush\config.json`

```bash
hush --config /path/to/config.json "你好"
```

可在 JSON 中设置 `"hush_mode": "focus"` 等；也可用 `"hush_calm_mode": false` 映射为 `plain`（兼容旧配置）。LLM 相关键名与环境变量对应关系见 [docs/configuration.md](docs/configuration.md)。

---

## 使用速查

| 场景 | 命令 |
|------|------|
| 单次 | `hush "问题"` |
| 管道 | `echo "问题" \| hush` |
| 交互 REPL | `hush`（欢迎语随模式变化） |
| 切换模式 | `hush --mode hype "冲一把"` 或 `export HUSH_MODE=focus` |
| 反 PUA 演练 | `hush --mode pua "…"` 或 `export HUSH_MODE=pua`（环境变量可用别名 `anti-pua` 等，见 [配置说明](docs/configuration.md)） |
| 仅基础提示 | `hush --mode plain` 或 `--no-calm`（兼容） |
| 版本 | `hush --version` |
| 脚本解析错误 | `hush --json-errors "问"`（stderr 单行 JSON） |

完整参数、TTY/管道分支、退出码： **[docs/cli.md](docs/cli.md)**。

---

## 常见问题

<details>
<summary><strong>提示未配置 API 密钥</strong></summary>

设置 `LLM_APPKEY`，或在配置文件中填写 `llm_appkey`。见 [配置文档](docs/configuration.md)。

</details>

<details>
<summary><strong>管道无输出或立刻退出</strong></summary>

无参数且 stdin **不是**交互终端时，会从 stdin 读入；若去空白后为空，会报错退出。

</details>

<details>
<summary><strong>想换模型或自建网关</strong></summary>

使用 `LLM_MODEL`、`OPENAI_BASE_URL` 或 JSON 中对应字段。

</details>

<details>
<summary><strong>为什么永远只有「一句话」？</strong></summary>

这是产品设计：客户端只展示首句（或首行截断）。详见 [docs/architecture.md](docs/architecture.md)。

</details>

<details>
<summary><strong>几种模式有什么区别？</strong></summary>

`calm`/`focus`/`hype` 在系统提示中追加不同前缀，`plain` 不加；`pua` 使用**独立**演练提示（不叠用「哲理老人」）。客户端仍只输出 **一句话**。详见 [docs/configuration.md](docs/configuration.md)。

</details>

<details>
<summary><strong><code>pua</code> 模式适合做什么？有什么限制？</strong></summary>

用于在受控、教育语境下**练习识别**操控话术、边界与回应思路：模型按提示输出**一句**虚构的「施压方」台词。它不是心理咨询、也不是对真实关系的诊断；若你面临暴力、跟踪、职场/亲密关系中的现实风险，请向专业人士与本地求助渠道求助。详见 [docs/configuration.md](docs/configuration.md) 与 [SECURITY.md](SECURITY.md)。

</details>

---

## 贡献

我们欢迎 Issue 与 Pull Request。

```bash
pip install -e ".[dev]"
make check
```

流程与 CI 说明见 **[CONTRIBUTING.md](CONTRIBUTING.md)**。若你改善文档、测试或 CLI 体验，同样非常感谢。

---

## 社区、安全与许可证

| 资源 | 链接 |
|------|------|
| 行为准则 | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| 贡献指南 | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 安全披露 | [SECURITY.md](SECURITY.md) |
| 治理 | [GOVERNANCE.md](GOVERNANCE.md) |
| 维护者与发版 | [MAINTAINERS.md](MAINTAINERS.md) |
| 变更记录 | [CHANGELOG.md](CHANGELOG.md) |

**许可证：** [Apache License 2.0](LICENSE) · 归属见 [NOTICE](NOTICE)

---

## English

**hush.ai** is a minimal terminal CLI for a **zen, one-sentence** AI reply. It uses the **OpenAI Python SDK** against an **OpenAI-compatible** Chat Completions endpoint. Set **`LLM_APPKEY`** (or `llm_appkey` in JSON); optionally **`OPENAI_BASE_URL`** and **`LLM_MODEL`** for third-party gateways (defaults: official OpenAI host + `gpt-4o-mini` when unset). See the **「LLM 接入说明」** section in the Chinese README above, or [docs/configuration.md](docs/configuration.md). Client-side post-processing keeps output to a **single sentence** (first sentence by punctuation; otherwise first line, truncated).

**Modes:** `calm` (anti-anxiety, default), `focus` (anti-procrastination), `hype` (motivational), `plain` (base prompt only), `pua` (educational drill: one fictional pressure line for awareness practice; **not** therapy or crisis support). Set via `--mode`, `HUSH_MODE`, or `hush_mode` in JSON. **Aliases** (env / JSON only, not `--mode`): e.g. `anti-anxiety`→`calm`, `anti-pua`→`pua` — see [docs/configuration.md](docs/configuration.md). Legacy: `HUSH_CALM_MODE=0` or `--no-calm` → `plain`.

**Highlights:** mode switching, timeouts & retries, Chinese SDK error messages, JSON config + env overrides, stdin piping, REPL, `--json-errors` for scripts.

| Resource | Link |
|----------|------|
| Documentation hub | [docs/README.md](docs/README.md) |
| Configuration | [docs/configuration.md](docs/configuration.md) |
| CLI reference | [docs/cli.md](docs/cli.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Security | [SECURITY.md](SECURITY.md) |

**License:** [Apache-2.0](LICENSE)
