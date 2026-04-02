# 命令行参考

## 命令与入口

安装包后使用 **`hush`**；亦可 **`python -m hushai`**（等价）。

```bash
hush [选项] [问题...]
```

## 选项

| 选项 | 说明 |
|------|------|
| `-h`, `--help` | 显示帮助并退出（退出码 0） |
| `--version` | 显示版本并退出（退出码 0） |
| `-c PATH`, `--config PATH` | 指定 JSON 配置文件；若文件不存在则报错 |
| `--json-errors` | 将错误以 **单行 JSON** 输出到 stderr：`{"error":"..."}`，便于脚本解析 |
| `--mode MODE` | `calm` / `focus` / `hype` / `plain` / `pua`；写入 `HUSH_MODE`，覆盖配置文件 |
| `--no-calm` | 与 `--mode plain` 互斥；等价于仅基础提示（兼容旧参数） |

`--mode` 的合法取值为 **`calm` / `focus` / `hype` / `plain` / `pua` 五个规范名**（argparse `choices`）。若需在脚本里使用**别名**（如 `anti-pua`→`pua`），请设置环境变量 `HUSH_MODE` 或 JSON `hush_mode`，见 [配置说明 · 模式别名](configuration.md#mode-aliases)。

## 位置参数 `问题...`

- 若 **提供** 任意非空参数：将参数用空格连接成一条字符串，作为**单次提问**（仍会经「一句话」后处理）。
- 若 **不提供**：进入「无参数」模式，行为见下节。

## 无参数时的三种分支

<a id="no-arg-branches"></a>

`hush` 且不带 `问题...` 时：

1. **标准输入是终端（TTY）** → 进入 **交互式 REPL**，提示符为 `>`，输入 `exit` / `quit` / `q` 退出。欢迎语随 `HUSH_MODE` 变化（`calm` / `focus` / `hype` / `plain` / `pua` 各一句，见 `hushai/cli.REPL_WELCOME`）。
2. **标准输入不是 TTY**（例如管道、重定向）→ 读取 **stdin 全部内容**，去首尾空白后作为单次提问；若去空白后为空，则报错退出。
3. 配置加载失败（如 `--config` 路径不存在、JSON 非法）→ 报错退出，不进入 REPL。

## 管道与示例

```bash
# 单次提问
hush "最近有些焦虑"

# 从管道读入（非 TTY）
echo "心乱时先做什么？" | hush

# 指定配置
hush -c ~/.config/hush/config.json "你好"

# 版本
hush --version

# 反 PUA 演练（单次；输出仍为客户端「一句话」）
hush --mode pua "同事常说我想太多，换一句他可能甩过来的话"
```

## 标准输出与标准错误

- **成功**：模型回复经客户端截断为「一句话」后，**仅一行**打印到 **stdout**（不含多余换行段落）。
- **失败**：人类可读文案或 `--json-errors` 的 JSON 写到 **stderr**。

## 退出码

| 码 | 含义 |
|----|------|
| `0` | 成功（含 `--help` / `--version`、REPL 正常退出、EOF 退出） |
| `1` | 配置错误、缺少密钥、API/网络类错误、stdin 为空、REPL 中单次请求失败等 |

脚本中建议：`hush ... || echo "failed with $?"`

## 「一句话」规则（客户端）

与 [架构说明](architecture.md) 中后处理一致：按句末标点取首句；无句末标点则取首行并最多 300 字符。
