import os
import json
import google.generativeai as genai
from app.schemas.profile import OnboardingSubmission, ProfileDimensions

class ProfileAnalyzer:
    def __init__(self):
        # 初始化 Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(
            model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            generation_config={"response_mime_type": "application/json"}
        )

    async def analyze_onboarding_data(self, data: OnboardingSubmission) -> ProfileDimensions:
        # 构造给 AI 的提示词（System Prompt 思想）
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
            # 调用 Gemini API
            response = await self.model.generate_content_async(prompt)
            
            # 解析 JSON 响应
            result_dict = json.loads(response.text)
            
            # 使用 Pydantic 进行校验和转换
            return ProfileDimensions(**result_dict)
            
        except Exception as e:
            import logging
            logging.getLogger("edunexus").error(f"Gemini Analysis Error: {e}", exc_info=True)
            # 兜底逻辑：如果 AI 失败，返回一组默认值，保证业务不中断
            return ProfileDimensions(
                knowledge_base_score=50,
                cognitive_style="均衡型",
                error_preference="通用逻辑瓶颈",
                learning_goals="持续提升",
                focus_duration=30,
                stress_resistance=50
            )

# 导出单例
analyzer = ProfileAnalyzer()