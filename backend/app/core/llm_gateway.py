"""
Mini LLM Gateway — 统一拦截 LLM 调用，支持 Demo 模式直返 fallback。

使用方式:
    from app.core.llm_gateway import llm_gateway
    result = await llm_gateway.call(prompt, agent_type, topic, profile)
    # result = {"content": <dict>, "source": "fallback" | "deepseek"}

Demo 模式 (.env DEMO_MODE=true):
    跳过所有真实 API 调用，直接返回 ContentGenerator._get_fallback()。
"""

import json
import logging
from typing import Any

import requests

from app.core.config import settings

logger = logging.getLogger("edunexus.llm_gateway")


class LLMGateway:
    def __init__(self) -> None:
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        }

    async def call(
        self,
        prompt: str,
        agent_type: str,
        topic: str,
        profile: dict | None = None,
        fallback_fn: Any = None,
    ) -> dict:
        """
        统一入口：根据 DEMO_MODE 决定走真实 API 还是 fallback。

        Returns:
            {"content": <dict>, "source": "fallback" | "deepseek"}
        """
        if settings.DEMO_MODE:
            logger.info(f"[LLM Gateway] DEMO_MODE: returning fallback for agent={agent_type}, topic={topic}")
            content = fallback_fn(agent_type, topic) if fallback_fn else {}
            return {"content": content, "source": "fallback"}

        return await self._call_deepseek(prompt, agent_type, topic, fallback_fn)

    # ---- internal ----

    async def _call_deepseek(
        self,
        prompt: str,
        agent_type: str,
        topic: str,
        fallback_fn: Any,
    ) -> dict:
        """调用真实 DeepSeek API，失败时降级到 fallback。"""
        try:
            payload = {
                "model": settings.DEEPSEEK_MODEL,
                "messages": [
                    {"role": "system", "content": "你是一位专业的教育内容生成专家。请严格按照指定的格式和要求生成内容。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 4000,
            }

            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            content_text = data["choices"][0]["message"]["content"]

            # 尝试解析 JSON
            try:
                content = json.loads(content_text)
                logger.info(f"[LLM Gateway] DeepSeek success for agent={agent_type}")
                return {"content": content, "source": "deepseek"}
            except json.JSONDecodeError:
                logger.warning(f"[LLM Gateway] DeepSeek returned non-JSON, wrapping as text")
                return {"content": {"content": content_text}, "source": "deepseek"}

        except Exception as e:
            logger.warning(f"[LLM Gateway] DeepSeek call failed: {e} — falling back")
            content = fallback_fn(agent_type, topic) if fallback_fn else {}
            return {"content": content, "source": "fallback"}


llm_gateway = LLMGateway()
