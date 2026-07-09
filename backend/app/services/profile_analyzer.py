import json
import logging
import aiohttp

from app.schemas.profile import OnboardingSubmission, ProfileDimensions
from app.core.config import settings

logger = logging.getLogger("edunexus")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


class ProfileAnalyzer:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL

    async def analyze_onboarding_data(self, data: OnboardingSubmission) -> ProfileDimensions:
        prompt = f"""
        你是一个资深教育心理学家和 AI 导师。
        请根据以下学生的 4 维度原始调查数据，分析并生成一个包含 6 个核心维度的结构化学生画像。

        原始数据:
        {json.dumps(data.responses, ensure_ascii=False)}

        请输出以下 JSON 格式：
        {{
            "knowledge_base_score": 整数(0-100，基于其掌握的知识基础估算),
            "cognitive_style": "字符串(如：视觉型、代码实践型、理论推导型等)",
            "error_preference": "字符串(描述学生最容易在哪些地方遇到挫败或逻辑瓶颈)",
            "learning_goals": "字符串(简短描述其核心学习动力)",
            "focus_duration": 整数(单位分钟，基于其时间分布习惯估算),
            "stress_resistance": 整数(0-100，抗压与韧性分值)
        }}
        """

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位资深教育心理学家和AI导师。请严格按照JSON格式输出分析结果。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        timeout = aiohttp.ClientTimeout(total=60, connect=15, sock_read=30)

        try:
            logger.info("Calling DeepSeek API for profile analysis")
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    DEEPSEEK_API_URL, json=payload, headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw_content = data["choices"][0]["message"]["content"].strip()
                        logger.info(f"DeepSeek profile analysis response (first 300 chars): {raw_content[:300]}")
                        result_dict = json.loads(raw_content)
                        return ProfileDimensions(**result_dict)
                    else:
                        error_text = await resp.text()
                        logger.error(f"DeepSeek API error {resp.status}: {error_text[:500]}")
                        raise RuntimeError(f"DeepSeek API returned {resp.status}")

        except Exception as e:
            logger.error(f"Profile analysis failed: {e}", exc_info=True)
            return ProfileDimensions(
                knowledge_base_score=50,
                cognitive_style="均衡型",
                error_preference="通用逻辑瓶颈",
                learning_goals="持续提升",
                focus_duration=30,
                stress_resistance=50
            )


analyzer = ProfileAnalyzer()
