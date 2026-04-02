"""将模型回复压缩为「一句话」。"""

from __future__ import annotations

import re

# 与计划一致：按中英文句末标点拆分
_SENTENCE_SPLIT = re.compile(r"([。！？?!])")

# 无句末标点时，单行最大长度兜底
_MAX_FALLBACK_LEN = 300


def to_one_sentence(text: str) -> str:
    """
    取第一个完整句子（含句末标点）；若无句末标点则取第一行并截断。
    """
    if not text:
        return ""
    text = text.strip()
    if not text:
        return ""

    parts = _SENTENCE_SPLIT.split(text)
    # split 含捕获组时：["片段", "。", "剩余", ...]
    if len(parts) == 1:
        first_line = text.split("\n", 1)[0].strip()
        if len(first_line) > _MAX_FALLBACK_LEN:
            return first_line[:_MAX_FALLBACK_LEN]
        return first_line

    if len(parts) >= 2 and parts[1] in "。！？?!":
        return (parts[0] + parts[1]).strip()

    # 理论上当前正则下不会走到这里；保留为防御性分支
    return parts[0].strip()[:_MAX_FALLBACK_LEN]  # pragma: no cover
