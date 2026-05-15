import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
import json
from google.genai import Client
from app.schemas.profile import OnboardingSubmission, ProfileDimensions
from app.core.config import settings


class ProfileAnalyzer:
    def __init__(self):
        api_key = settings.GOOGLE_API_KEY
        if api_key:
            self.client = Client(api_key=api_key)
        else:
            self.client = None

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

        try:
            if self.client is None:
                raise RuntimeError("Gemini API not configured")

            response = await self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            result_dict = json.loads(response.text)
            return ProfileDimensions(**result_dict)

        except Exception as e:
            import logging
            logging.getLogger("edunexus").error(f"Gemini Analysis Error: {e}", exc_info=True)
            return ProfileDimensions(
                knowledge_base_score=50,
                cognitive_style="均衡型",
                error_preference="通用逻辑瓶颈",
                learning_goals="持续提升",
                focus_duration=30,
                stress_resistance=50
            )


analyzer = ProfileAnalyzer()
