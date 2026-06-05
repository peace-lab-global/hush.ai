"""安全过滤模块 - 危机信号检测与用户反馈。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


CRISIS_PATTERNS = [
    r"想死|不想活了|活着没意思|活着好累|不想活",
    r"自杀|自残|自己了结",
    r"杀人|想杀掉|弄死",
    r"绝症|晚期|活不了多久",
    r"报复社会|伤害他人",
]


@dataclass
class SafetyResult:
    is_safe: bool
    level: str
    message: Optional[str]
    suggestion: Optional[str]


HELP_MESSAGE = (
    "我注意到你可能正在经历困难时刻。请相信，你的感受是被看见的。\n\n"
    "如果你愿意，我可以继续陪伴你聊天。但我更希望你能够：\n"
    "• 拨打心理援助热线：全国心理援助热线 400-161-9995\n"
    "• 联系身边信任的人\n"
    "• 寻求专业心理咨询师的帮助\n\n"
    "你不需要独自面对一切。"
)


EMERGENCY_MESSAGE = (
    "我非常担心你的安全。\n\n"
    "如果你有立即的危险，请：\n"
    "• 拨打 120 急救\n"
    "• 拨打 110 报警\n"
    "• 前往最近医院的急诊室\n\n"
    "请让我知道你是否安全，或者你是否能够联系到可以帮助你的人。"
)


def check_safety(text: str) -> SafetyResult:
    text_lower = text.lower()

    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, text_lower):
            if "杀人" in text_lower or "报复" in text_lower:
                return SafetyResult(
                    is_safe=False,
                    level="emergency",
                    message="我注意到你提到了可能伤害自己或他人的想法。",
                    suggestion=EMERGENCY_MESSAGE,
                )
            return SafetyResult(
                is_safe=False,
                level="crisis",
                message="我注意到你可能正在经历很艰难的时刻。",
                suggestion=HELP_MESSAGE,
            )

    return SafetyResult(is_safe=True, level="safe", message=None, suggestion=None)


def format_safety_message(result: SafetyResult, original_reply: str) -> str:
    if result.is_safe:
        return original_reply

    warning = f"【温馨提示】{result.message}\n\n{result.suggestion}"
    return f"{original_reply}\n\n---\n{warning}"
