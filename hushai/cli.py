"""`hush` 命令行：一次性提问、管道输入或交互式 REPL。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Final

from hushai import __version__
from hushai.llm import chat_once
from hushai.postprocess import to_one_sentence
from hushai.settings import configure, get_mode

REPL_WELCOME: Final[dict[str, str]] = {
    "calm": "hush — 慢慢来，一句就好；心里乱也可以说。输入 exit / quit / q 退出。",
    "focus": "hush — 先做最小一步，一句定方向。输入 exit / quit / q 退出。",
    "hype": "hush — 一口气，一句话，往前顶一顶。输入 exit / quit / q 退出。",
    "plain": "hush — 问一句，答一句。输入 exit / quit / q 退出。",
    "pua": "hush — 反PUA演练：对方可能甩来一句带刺的话，练觉察。输入 exit / quit / q 退出。",
}


def _print_zen_line(raw: str) -> None:
    line = to_one_sentence(raw)
    print(line)


def _emit_error(message: str, *, json_errors: bool) -> None:
    if json_errors:
        print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    else:
        print(message, file=sys.stderr)


def _stdin_text_if_piped() -> str | None:
    """若在管道中则读取 stdin；否则返回 None 表示进入 REPL。"""
    if sys.stdin.isatty():
        return None
    return sys.stdin.read()


def run_repl(*, json_errors: bool = False) -> int:
    print(REPL_WELCOME[get_mode()])
    while True:
        try:
            user = input("> ").strip()
        except EOFError:
            print()
            return 0
        if not user:
            continue
        lower = user.lower()
        if lower in ("exit", "quit", "q"):
            return 0
        try:
            raw = chat_once(user)
        except RuntimeError as e:
            _emit_error(str(e), json_errors=json_errors)
            return 1
        except Exception as e:
            _emit_error(f"请求失败: {e}", json_errors=json_errors)
            return 1
        _print_zen_line(raw)


def run_once(question: str, *, json_errors: bool = False) -> int:
    try:
        raw = chat_once(question)
    except RuntimeError as e:
        _emit_error(str(e), json_errors=json_errors)
        return 1
    except Exception as e:
        _emit_error(f"请求失败: {e}", json_errors=json_errors)
        return 1
    _print_zen_line(raw)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hush",
        description=(
            "禅意 AI CLI：配置 LLM_APPKEY；支持多模式（反焦虑/反拖延/激励/仅基础/反PUA演练），"
            "每次只回答一句话。"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--config",
        "-c",
        metavar="PATH",
        help="配置文件路径（JSON）；亦可设置环境变量 HUSH_CONFIG",
    )
    parser.add_argument(
        "--json-errors",
        action="store_true",
        help="将错误以单行 JSON 输出到 stderr",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--mode",
        choices=["calm", "focus", "hype", "plain", "pua"],
        default=None,
        metavar="MODE",
        help=("对话模式：calm / focus / hype / plain / pua；覆盖环境变量 HUSH_MODE"),
    )
    mode_group.add_argument(
        "--no-calm",
        action="store_true",
        help="等价于 --mode plain（兼容旧参数）",
    )
    parser.add_argument(
        "question",
        nargs="*",
        help="可选：一次性提问；省略且 stdin 为终端时进入交互模式；管道时可从 stdin 读入",
    )
    args = parser.parse_args(argv)

    if args.mode is not None:
        os.environ["HUSH_MODE"] = args.mode
    elif args.no_calm:
        os.environ["HUSH_MODE"] = "plain"

    try:
        configure(args.config)
    except RuntimeError as e:
        _emit_error(str(e), json_errors=args.json_errors)
        return 1

    if args.question:
        return run_once(" ".join(args.question).strip(), json_errors=args.json_errors)

    piped = _stdin_text_if_piped()
    if piped is not None:
        text = piped.strip()
        if not text:
            _emit_error("标准输入为空。", json_errors=args.json_errors)
            return 1
        return run_once(text, json_errors=args.json_errors)

    return run_repl(json_errors=args.json_errors)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
