import json
from google import genai
from google.genai import types
from app.schemas.profile import ProfileDimensions
from app.core.config import settings


class PathPlanner:
    """使用 Gemini 根据学习目标和学生画像生成个性化 DAG 学习路径"""

    def __init__(self):
        api_key = settings.GOOGLE_API_KEY
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

    async def plan_path(self, goal: str, profile: ProfileDimensions | dict | None = None) -> dict:
        profile_context = ""
        weak_areas = []
        if profile:
            if isinstance(profile, dict):
                kb = profile.get('knowledge_base_score', 50)
                cs = profile.get('cognitive_style', 'N/A')
                ep = profile.get('error_preference', 'N/A')
                lg = profile.get('learning_goals', 'N/A')
                fd = profile.get('focus_duration', 30)
                sr = profile.get('stress_resistance', 50)
                profile_context = f"""
            学生画像: 知识基础{kb}/100分,
            认知风格{cs}, 易错偏好{ep},
            学习目标{lg}, 专注时长{fd}min,
            抗压值{sr}/100
            """
                if kb < 60:
                    weak_areas.append("基础知识薄弱")
                if sr < 50:
                    weak_areas.append("抗压能力需加强")
            else:
                profile_context = f"""
            学生画像: 知识基础{profile.knowledge_base_score}/100分,
            认知风格{profile.cognitive_style}, 易错偏好{profile.error_preference},
            学习目标{profile.learning_goals}, 专注时长{profile.focus_duration}min,
            抗压值{profile.stress_resistance}/100
            """
                if profile.knowledge_base_score < 60:
                    weak_areas.append("基础知识薄弱")
                if profile.stress_resistance < 50:
                    weak_areas.append("抗压能力需加强")

        prompt = f"""你是一位资深课程设计师和AI教育专家。
        请根据学习目标生成一个个性化DAG学习路径。

        学习目标: {goal}
        {profile_context}

        请输出以下JSON:
        {{
            "title": "学习路径标题",
            "analysis_summary": "基于学生画像的分析总结，指出薄弱环节和注入节点原因(100字以内)",
            "nodes": [
                {{"id": "node-1", "label": "知识点名称", "type": "standard", "proficiency": 0.8, "status": "pending"}},
                ...
            ],
            "edges": [
                {{"from": "node-1", "to": "node-2", "isDynamic": false}},
                ...
            ]
        }}

        要求:
        - 生成 4-6 个知识节点，形成有向无环图
        - 如果学生有薄弱领域，插入 type="injected" 的补充节点(1-2个)
        - 每个节点的 proficiency 值基于画像估算
        - 第一个节点为 "completed"，第二第三个为 "active"，后续为 "pending"
        """

        if self.client is None:
            return self._get_fallback(goal, profile)

        try:
            response = await self.client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception:
            return self._get_fallback(goal, profile)

    def _get_fallback(self, goal: str, profile: ProfileDimensions | dict | None = None) -> dict:
        if isinstance(profile, dict):
            has_weakness = profile and profile.get('knowledge_base_score', 50) < 60
        else:
            has_weakness = profile and profile.knowledge_base_score < 60
        nodes = [
            {"id": "n1", "label": f"{goal}前置基础", "type": "standard", "proficiency": 0.85, "status": "completed"},
            {"id": "n1b", "label": "数学基础强化 (AI注入)", "type": "injected", "proficiency": 0.45, "status": "active"},
            {"id": "n2", "label": f"{goal}核心原理", "type": "standard", "proficiency": 0.6, "status": "active"},
            {"id": "n3", "label": f"{goal}进阶应用", "type": "standard", "proficiency": 0.3, "status": "pending"},
            {"id": "n4", "label": f"{goal}实战项目", "type": "standard", "proficiency": 0.0, "status": "pending"},
        ]
        edges = [
            {"from": "n1", "to": "n1b", "isDynamic": True},
            {"from": "n1", "to": "n2", "isDynamic": False},
            {"from": "n1b", "to": "n2", "isDynamic": True},
            {"from": "n2", "to": "n3", "isDynamic": False},
            {"from": "n3", "to": "n4", "isDynamic": False},
        ]
        if not has_weakness:
            nodes = [n for n in nodes if n["type"] != "injected"]
            edges = [e for e in edges if not e.get("isDynamic")]

        return {
            "title": f"{goal} 学习路径",
            "analysis_summary": f"根据你的画像分析，{'基础知识需要补充，已在路径中注入强化节点' if has_weakness else '基础知识扎实，可以直接进入核心学习'}。当前路径共 {len(nodes)} 个阶段。",
            "nodes": nodes,
            "edges": edges,
        }


planner = PathPlanner()
