"""OpenAI Chat Completions 调用（通过 LLM_APPKEY / 配置文件）。"""

from __future__ import annotations

from typing import Any, Final

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    PermissionDeniedError,
    RateLimitError,
)

from hushai.settings import (
    get_api_key,
    get_base_url,
    get_max_retries,
    get_mode,
    get_model,
    get_timeout_seconds,
)

SYSTEM_PROMPT_BASE: Final[str] = (
    "你是一位沉静、通透的哲理老人，说话像禅语：不教训人，只轻轻点一下。"
    "始终用简体中文回答。"
    "无论对方说什么，你只回答一句话，不要换行，不要分点，不要引号包裹整句。"
)

# 反焦虑：柔、稳、接纳
ANTI_ANXIETY_PROMPT: Final[str] = (
    "【反焦虑】对方可能带着紧张、担忧或自我批评而来：先接纳情绪，不否定、不轻视；"
    "语气平稳、句子简短，避免制造紧迫感或灾难化联想；"
    "不堆砌建议，若需行动只点一个最小可行步；"
    "不用「你必须」「你应该」等命令式，不加重羞耻或自责。"
)

# 反拖延：小步、当下、不羞辱
ANTI_PROCRASTINATION_PROMPT: Final[str] = (
    "【反拖延】对方可能拖延、回避或陷入完美主义：不指责、不羞辱；"
    "把目标收成此刻就能做的最小一步，避免开长清单；"
    "语气稳而利落；仍只回答一句话。"
)

# 打鸡血：积极、短促、拒绝空洞口号
HYPE_PROMPT: Final[str] = (
    "【激励】对方需要一点推动力：语气积极、有力量，但要真诚、具体；"
    "避免空洞口号、毒鸡汤和贬低式激将；"
    "仍只回答一句话。"
)

MODE_SUFFIXES: Final[dict[str, str]] = {
    "calm": ANTI_ANXIETY_PROMPT,
    "focus": ANTI_PROCRASTINATION_PROMPT,
    "hype": HYPE_PROMPT,
    "plain": "",
    "pua": "",
}

# 独立系统提示：不叠用「哲理老人」，避免与施压者角色扮演冲突
PUA_DRILL_SYSTEM: Final[str] = (
    "【反PUA演练】教育向安全模拟，用于识别操控话术与心理边界，不能替代专业心理咨询或法律援助。"
    "根据用户描述或问题，用**简体中文**只输出**一句话**："
    "扮演对话里「施压一方」可能说出的一句台词，可轻度体现贬低、甩锅、愧疚诱导或煤气灯式表述，"
    "但必须克制、虚构情境、不涉性、不侮辱人格、不用脏话、不针对任何真实个人；"
    "不要换行，不要分点，不要引号包裹整句，不要加旁白或解释这是演练。"
)


def build_system_prompt() -> str:
    mode = get_mode()
    if mode == "pua":
        return PUA_DRILL_SYSTEM
    suffix = MODE_SUFFIXES.get(mode, "")
    return SYSTEM_PROMPT_BASE + suffix


def format_openai_error(exc: Any) -> str:
    """将 OpenAI SDK 异常转换为用户可读中文说明。"""
    if isinstance(exc, APITimeoutError):
        return "请求超时，请检查网络或增大 LLM_TIMEOUT。"
    if isinstance(exc, APIConnectionError):
        return "无法连接到 API 服务，请检查网络与 OPENAI_BASE_URL。"
    if isinstance(exc, RateLimitError):
        return "请求过于频繁，请稍后再试。"
    if isinstance(exc, AuthenticationError):
        return "API 密钥无效或无权访问，请检查 LLM_APPKEY。"
    if isinstance(exc, PermissionDeniedError):
        return "权限不足，请检查账户权限或模型访问策略。"
    if isinstance(exc, APIStatusError):
        return f"服务端返回错误（HTTP {exc.status_code}）。"
    if isinstance(exc, OpenAIError):
        return f"请求失败: {exc}"
    return f"请求失败: {exc}"


def chat_once(user_message: str) -> str:
    """
    调用一次对话，返回模型原始文本（未做单句后处理）。
    """
    api_key = get_api_key()
    if not api_key:
        msg = (
            "未配置 API 密钥：请设置环境变量 LLM_APPKEY，"
            "或在配置文件（见 README）中填写 llm_appkey。"
        )
        raise RuntimeError(msg)

    base_url = get_base_url()
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=get_timeout_seconds(),
        max_retries=get_max_retries(),
    )

    model = get_model()
    extra_body: dict[str, Any] | None = None
    if "kimi-k2" in model:
        extra_body = {"thinking": {"type": "enabled"}}

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": user_message},
            ],
            extra_body=extra_body,
        )
    except OpenAIError as e:
        raise RuntimeError(format_openai_error(e)) from None

    choice = response.choices[0]
    content = choice.message.content
    if content is None:
        return ""
    return content
