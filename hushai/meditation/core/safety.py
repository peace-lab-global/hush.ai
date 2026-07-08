"""安全过滤模块 - 危机信号检测与用户反馈。

检测分两类级别：
- ``crisis``     : 用户表露自伤/自杀倾向，需温和引导并给出心理援助热线。
- ``emergency``  : 用户表露伤害他人/报复社会的倾向，需立即给出紧急求助信息。

注意：本模块基于关键词正则，是「快速阻断层」而非完整危机识别系统。
中文字符无大小写之分，``text.lower()`` 对中文无意义；英文关键词的大小写
不敏感由 ``re.IGNORECASE`` 保证。关键词列表会持续迭代。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

# 每条规则为 (编译后的正则, 命中级别)。级别与触发模式在编译期绑定，
# 避免「先匹配再二次判级别」导致的判定与模式脱钩问题。
# order matters: 更具体的「伤害他人」规则放在自伤规则之前，确保 emergency
# 能优先于 crisis 命中（虽然任意一条命中即阻断，但级别会决定给用户的文案）。
_CRISIS_RULES: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"杀人|想杀掉|弄死|报复社会|伤害他人|想伤害别人", re.IGNORECASE),
        "emergency",
    ),
    (
        re.compile(r"想死|不想活了|活着没意思|活着好累|不想活|活不下去|了结自己", re.IGNORECASE),
        "crisis",
    ),
    (
        re.compile(r"自杀|自残|自己了结|割腕|跳楼|轻生", re.IGNORECASE),
        "crisis",
    ),
    (
        re.compile(r"绝症|晚期|活不了多久", re.IGNORECASE),
        "crisis",
    ),
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


# 级别 -> (面向用户的话术, 建议信息)。集中管理，避免散落分支。
_LEVEL_MESSAGES: dict[str, tuple[str, str]] = {
    "crisis": (
        "我注意到你可能正在经历很艰难的时刻。",
        HELP_MESSAGE,
    ),
    "emergency": (
        "我注意到你提到了可能伤害自己或他人的想法。",
        EMERGENCY_MESSAGE,
    ),
}


def check_safety(text: str) -> SafetyResult:
    """检查输入文本是否含危机信号。

    命中任意规则即按**该规则绑定的级别**返回；多条规则同时命中时取第一条
    （``_CRISIS_RULES`` 已按优先级排序）。未命中返回 ``is_safe=True``。
    """
    if not text:
        return SafetyResult(is_safe=True, level="safe", message=None, suggestion=None)

    for regex, level in _CRISIS_RULES:
        if regex.search(text):
            message, suggestion = _LEVEL_MESSAGES[level]
            return SafetyResult(
                is_safe=False,
                level=level,
                message=message,
                suggestion=suggestion,
            )

    return SafetyResult(is_safe=True, level="safe", message=None, suggestion=None)


def format_safety_message(result: SafetyResult, original_reply: str) -> str:
    if result.is_safe:
        return original_reply

    warning = f"【温馨提示】{result.message}\n\n{result.suggestion}"
    return f"{original_reply}\n\n---\n{warning}" if original_reply else warning
