"""
日语输出模式插件 - Japanese Mode Plugin

在 LLM 请求前注入日语输出指令，让 AI 用日语回复并在末尾提供中文翻译。
动作/神态描写保持中文不翻译。默认启用，可按会话独立开关。
"""

from __future__ import annotations

import logging
from typing import ClassVar

from astrbot.api import star
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest

logger = logging.getLogger("astrbot")

KV_DISABLED = "japanese_disabled"

# 日语模式的 system prompt 指令
# 追加在已有 system prompt 末尾，优先级高于其他约束
JAPANESE_INSTRUCTION = """

# 📖 日语输出模式（已启用）
- 请用日语回复我，使用口语化、自然的日语表达。
- 动作和神态描写（如（翻白眼）、（叹气）、（啃法棍）等）保持中文，放在（）内，放在句子开头或插入句中，不要单独成行。
- 在回复的末尾，用「（翻译：...）」格式附上日语内容的中文翻译，**和正文写在同一行**，不要换行。
- 翻译仅翻译对话文本，不翻译动作描写部分。
- **整条回复保持紧凑，不要有多余的空白行。**
"""


class Main(star.Star):
    """日语输出模式插件"""

    # 缓存已确认开启的会话，避免重复判断 KV
    _confirmed_enabled: ClassVar[set[str]] = set()

    def __init__(self, context: star.Context, config: dict | None = None) -> None:
        self.context = context

    # =========================================================================
    # 指令
    # =========================================================================

    @filter.command("japanese")
    async def cmd_japanese(self, event: AstrMessageEvent, action: str = "") -> None:
        """日语模式开关。用法: /japanese on|off|status"""
        a = action.strip().lower()
        umo = event.unified_msg_origin

        if a == "on" or a == "enable":
            await self._kv_remove(KV_DISABLED, umo)
            self._confirmed_enabled.discard(umo)
            yield event.plain_result("日本語モードをオンにしました！(日语模式已开启)")

        elif a == "off" or a == "disable":
            await self._kv_add(KV_DISABLED, umo)
            self._confirmed_enabled.discard(umo)
            yield event.plain_result("日本語モードをオフにしました。(日语模式已关闭)")

        elif a == "status":
            disabled = await self.get_kv_data(KV_DISABLED, [])
            on = umo not in disabled if isinstance(disabled, list) else True
            yield event.plain_result(
                f"日语模式: {'✅ 开启' if on else '❌ 关闭'}\n"
                "使用 /japanese on|off 切换。"
            )

        else:
            yield event.plain_result(
                "用法:\n"
                "/japanese on     - 开启日语模式\n"
                "/japanese off    - 关闭\n"
                "/japanese status - 查看状态"
            )

    # =========================================================================
    # LLM 请求拦截：注入日语指令
    # =========================================================================

    @filter.on_llm_request()
    async def inject_japanese(
        self, event: AstrMessageEvent, req: ProviderRequest
    ) -> None:
        """在 LLM 请求前检查日语模式，注入输出指令。"""
        try:
            umo = event.unified_msg_origin

            # 检查是否已确认开启（缓存加速）
            if umo in self._confirmed_enabled:
                req.system_prompt = (req.system_prompt or "") + JAPANESE_INSTRUCTION
                return

            # 检查 KV
            disabled = await self.get_kv_data(KV_DISABLED, [])
            if isinstance(disabled, list) and umo in disabled:
                return  # 已关闭，跳过

            # 开启状态 → 注入指令
            self._confirmed_enabled.add(umo)
            req.system_prompt = (req.system_prompt or "") + JAPANESE_INSTRUCTION

        except Exception:
            logger.exception("[japanese] 注入异常，已跳过本次")

    # =========================================================================
    # 内部方法
    # =========================================================================

    async def _kv_add(self, key: str, val: str) -> None:
        d = await self.get_kv_data(key, [])
        if not isinstance(d, list):
            d = []
        if val not in d:
            d.append(val)
            await self.put_kv_data(key, d)

    async def _kv_remove(self, key: str, val: str) -> None:
        d = await self.get_kv_data(key, [])
        if isinstance(d, list) and val in d:
            d.remove(val)
            await self.put_kv_data(key, d)
