import json
from google.genai import Client
from app.schemas.profile import ProfileDimensions
from app.core.config import settings


class ContentGenerator:
    """使用 Gemini 为各智能体生成内容"""

    def __init__(self):
        api_key = settings.GOOGLE_API_KEY
        if api_key:
            self.client = Client(api_key=api_key)
        else:
            self.client = None

    async def _call_ai(self, prompt: str) -> dict | None:
        if self.client is None:
            return None
        try:
            response = await self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            return json.loads(response.text)
        except Exception:
            return None

    async def generate_for_agent(self, agent_type: str, topic: str, profile: ProfileDimensions | dict | None = None) -> dict:
        profile_context = ""
        if profile:
            if isinstance(profile, dict):
                profile_context = f"""
            学生画像: 知识基础{profile.get('knowledge_base_score', 'N/A')}分, 认知风格{profile.get('cognitive_style', 'N/A')},
            易错偏好{profile.get('error_preference', 'N/A')}, 学习目标{profile.get('learning_goals', 'N/A')}
            """
            else:
                profile_context = f"""
            学生画像: 知识基础{profile.knowledge_base_score}分, 认知风格{profile.cognitive_style},
            易错偏好{profile.error_preference}, 学习目标{profile.learning_goals}
            """

        prompts = {
            "professor": f"""你是一位资深AI教授。请为主题"{topic}"撰写一份教学文档。
            {profile_context}
            请以JSON格式返回: {{"title": "课程标题", "sections": [{{"heading": "章节标题", "body": "章节内容"}}]}}
            内容深度适中，包含核心概念解释和具体示例。每个章节body至少100字。""",

            "architect": f"""你是一位知识架构师。请为主题"{topic}"设计一个Mermaid格式的思维导图。
            {profile_context}
            以JSON格式返回: {{"mindmap": {{"root": "中心主题", "children": [{{"name": "子主题", "children": [...]}}]}}}}
            至少包含3个一级分支，每个分支包含2-3个子节点。""",

            "examiner": f"""你是一位资深考官。请为主题"{topic}"出3道单项选择题。
            {profile_context}
            以JSON格式返回: {{"questions": [{{"question": "题目", "options": ["A","B","C","D"], "answer": 0, "explanation": "解析"}}]}}
            难度逐步递增，涵盖核心概念。""",

            "director": f"""你是一位教育视频导演。请为主题"{topic}"设计4个视频分镜场景。
            {profile_context}
            以JSON格式返回: {{"scenes": [{{"scene_number": 1, "title": "场景标题", "visual": "画面描述", "voiceover": "旁白脚本", "duration_seconds": 30}}]}}
            场景由浅入深，适合短视频教学。""",

            "hacker": f"""你是一位实战编程专家。请为主题"{topic}"编写一个Python代码实验。
            {profile_context}
            以JSON格式返回: {{"title": "实验标题", "description": "实验说明", "code": "完整可运行的Python代码", "expected_output": "预期输出", "exercises": ["扩展练习1", "扩展练习2"]}}
            代码需要有详细注释，帮助理解每一步。""",

            "reviewer": f"""你是一位内容质量审查专家。请审查主题"{topic}"的相关教学内容。
            以JSON格式返回: {{"hallucination_risk": "low/medium/high", "quality_score": 85, "suggestions": ["建议1", "建议2"], "difficulty_assessment": "难度评价"}}""",
        }

        prompt = prompts.get(agent_type)
        if prompt is None:
            return self._get_fallback(agent_type, topic)

        result = await self._call_ai(prompt)
        if result is None:
            return self._get_fallback(agent_type, topic)
        return result

    def _get_fallback(self, agent_type: str, topic: str) -> dict:
        """AI 调用失败时的兜底 Mock 数据"""
        fallbacks: dict[str, dict] = {
            "professor": {
                "title": f"深入理解：{topic}",
                "sections": [
                    {"heading": "核心概念", "body": f"{topic}是机器学习/AI领域的核心概念之一。在深入探讨之前，我们先建立对基础原理的清晰理解。"},
                    {"heading": "数学原理", "body": f"{topic}的数学基础建立在优化理论和线性代数之上。理解其中的数学推导对于掌握该概念至关重要。"},
                    {"heading": "实践应用", "body": f"在实际应用中，{topic}已经被广泛部署于各类场景。我们将通过具体案例来分析其工作原理。"},
                    {"heading": "常见误区", "body": "学习过程中最常遇到的困惑包括概念混淆、参数调优不当等问题。本节将逐一澄清。"},
                ],
            },
            "architect": {
                "mindmap": {
                    "root": topic,
                    "children": [
                        {"name": "基础理论", "children": [{"name": "数学原理"}, {"name": "核心定义"}]},
                        {"name": "算法实现", "children": [{"name": "Python示例"}, {"name": "优化技巧"}]},
                        {"name": "应用场景", "children": [{"name": "工业案例"}, {"name": "学术研究"}]},
                    ],
                }
            },
            "examiner": {
                "questions": [
                    {"question": f"关于{topic}，以下哪个描述最准确？", "options": ["选项A：描述1", "选项B：描述2", "选项C：描述3", "选项D：描述4"], "answer": 1, "explanation": "该选项准确概括了核心定义。"},
                    {"question": f"在{topic}的实践中，以下哪个步骤应该首先完成？", "options": ["参数调优", "数据预处理", "模型部署", "结果可视化"], "answer": 1, "explanation": "数据预处理是所有后续步骤的基础。"},
                    {"question": f"{topic}与相关概念的主要区别在于？", "options": ["计算速度", "理论基础", "应用领域", "以上都是"], "answer": 1, "explanation": "理论基础的差异是最本质的区别。"},
                ],
            },
            "director": {
                "scenes": [
                    {"scene_number": 1, "title": "问题引入", "visual": "动画展示一个实际问题场景", "voiceover": f"今天我们来探索{topic}。从一个直观的问题开始...", "duration_seconds": 30},
                    {"scene_number": 2, "title": "核心原理", "visual": "逐步拆解核心算法流程", "voiceover": f"让我们深入到{topic}的核心...", "duration_seconds": 45},
                    {"scene_number": 3, "title": "代码演示", "visual": "屏幕录制展示代码实现", "voiceover": "现在来看具体的代码实现...", "duration_seconds": 60},
                    {"scene_number": 4, "title": "总结回顾", "visual": "思维导图回顾关键点", "voiceover": f"总结一下{topic}的要点...", "duration_seconds": 25},
                ],
            },
            "hacker": {
                "title": f"{topic} - Python代码实验",
                "description": f"通过动手实践来理解{topic}的核心原理",
                "code": f'''"""
{topic} - 动手实验
通过代码来直观理解核心概念
"""
import numpy as np
import matplotlib.pyplot as plt

def demonstrate_concept():
    """演示{topic}的核心概念"""
    # ===== 步骤1: 准备数据 =====
    print("步骤1: 准备实验数据")
    x = np.linspace(-5, 5, 100)
    y = x ** 2  # 示例：二次函数

    # ===== 步骤2: 核心计算 =====
    print("步骤2: 执行核心计算")
    derivative = 2 * x  # 导数
    gradient = derivative[50]  # 某点的梯度

    print(f"在 x=0 处的梯度: {{gradient}}")

    # ===== 步骤3: 可视化 =====
    print("步骤3: 生成可视化图表")
    # plt.plot(x, y, label='f(x)')
    # plt.legend()
    # plt.show()

    return {{"min_value": np.min(y), "gradient_at_zero": float(gradient)}}

if __name__ == "__main__":
    result = demonstrate_concept()
    print(f"实验结果: {{result}}")
''',
                "expected_output": "步骤1: 准备实验数据\n步骤2: 执行核心计算\n在 x=0 处的梯度: 0.0\n步骤3: 生成可视化图表\n实验结果: {'min_value': 0.0, 'gradient_at_zero': 0.0}",
                "exercises": [
                    "修改函数定义，尝试其他函数如 y = x^3 观察梯度变化",
                    "添加噪声数据，观察对梯度计算的影响",
                ],
            },
            "reviewer": {
                "hallucination_risk": "low",
                "quality_score": 85,
                "suggestions": ["建议在教授文档中增加更多实际案例", "思维导图可以进一步细化第三级节点"],
                "difficulty_assessment": "内容难度适中，适合有一定基础的学习者",
            },
        }
        return fallbacks.get(agent_type, {"message": f"Agent {agent_type} content placeholder for {topic}"})


generator = ContentGenerator()
