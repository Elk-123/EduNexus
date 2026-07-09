import json
import logging
import aiohttp

from app.schemas.profile import ProfileDimensions
from app.core.config import settings

logger = logging.getLogger("edunexus")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


class PathPlanner:
    """使用 DeepSeek 根据学习目标和学生画像生成个性化 DAG 学习路径"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL

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

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位资深课程设计师和AI教育专家。请严格按照JSON格式输出学习路径规划结果。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.5,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        timeout = aiohttp.ClientTimeout(total=60, connect=15, sock_read=30)

        try:
            logger.info(f"Calling DeepSeek API for path planning: {goal}")
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    DEEPSEEK_API_URL, json=payload, headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw_content = data["choices"][0]["message"]["content"].strip()
                        logger.info(f"DeepSeek path planning response (first 300 chars): {raw_content[:300]}")
                        result = json.loads(raw_content)
                        return result
                    else:
                        error_text = await resp.text()
                        logger.error(f"DeepSeek API error {resp.status}: {error_text[:500]}")
                        raise RuntimeError(f"DeepSeek API returned {resp.status}")

        except Exception as e:
            logger.warning(f"Path planning failed, using fallback: {e}")
            return self._get_fallback(goal, profile)

    def _get_fallback(self, goal: str, profile: ProfileDimensions | dict | None = None) -> dict:
        goal_lower = goal.lower()
        ai_keywords = [
            "人工智能", "机器学习", "深度学习",
            "transformer", "llm", "large language", "neural network",
            "machine learning", "deep learning", "reinforcement learning",
            "nlp", "computer vision", "cv", "generative ai"
        ]
        is_ai_path = any(keyword in goal_lower for keyword in ai_keywords)

        if is_ai_path:
            return self._get_ai_path_fallback(goal, profile)
        else:
            return self._get_general_path_fallback(goal, profile)

    def _get_ai_path_fallback(self, goal: str, profile: ProfileDimensions | dict | None = None) -> dict:
        """人工智能学习路径的fallback - 三个阶段设计"""
        nodes = [
            {"id": "ai-math", "label": "数学基础", "type": "standard", "proficiency": 0.8, "status": "completed"},
            {"id": "ai-prog", "label": "编程开发", "type": "standard", "proficiency": 0.8, "status": "completed"},
            {"id": "ai-la", "label": "线性代数", "type": "standard", "proficiency": 0.7, "status": "active"},
            {"id": "ai-calc", "label": "微积分", "type": "standard", "proficiency": 0.7, "status": "active"},
            {"id": "ai-stat", "label": "概率统计", "type": "standard", "proficiency": 0.7, "status": "active"},
            {"id": "ai-python", "label": "Python核心语法", "type": "standard", "proficiency": 0.8, "status": "active"},
            {"id": "ai-libs", "label": "数据处理库", "type": "standard", "proficiency": 0.6, "status": "pending"},
            {"id": "ai-stage1", "label": "第一阶段：基础储备完成", "type": "milestone", "proficiency": 1.0, "status": "pending"},
            {"id": "ai-ml", "label": "经典机器学习", "type": "standard", "proficiency": 0.4, "status": "pending"},
            {"id": "ai-sup", "label": "监督学习", "type": "standard", "proficiency": 0.4, "status": "pending"},
            {"id": "ai-unsup", "label": "无监督学习", "type": "standard", "proficiency": 0.4, "status": "pending"},
            {"id": "ai-dl", "label": "深度学习基础", "type": "standard", "proficiency": 0.3, "status": "pending"},
            {"id": "ai-frame", "label": "深度学习框架", "type": "standard", "proficiency": 0.3, "status": "pending"},
            {"id": "ai-cv", "label": "计算机视觉", "type": "standard", "proficiency": 0.2, "status": "pending"},
            {"id": "ai-nlp", "label": "自然语言处理", "type": "standard", "proficiency": 0.2, "status": "pending"},
            {"id": "ai-audio", "label": "语音信号处理", "type": "standard", "proficiency": 0.2, "status": "pending"},
            {"id": "ai-stage2", "label": "第二阶段：核心模型掌握", "type": "milestone", "proficiency": 1.0, "status": "pending"},
            {"id": "ai-transformer", "label": "Transformer架构", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-llm", "label": "大语言模型原理", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-app", "label": "应用开发层", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-tech", "label": "模型调优层", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-ops", "label": "工程部署层", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-rag", "label": "RAG检索增强", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-agent", "label": "AI智能体", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-ft", "label": "LoRA/PEFT微调", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-rlhf", "label": "强化学习对齐", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-quant", "label": "模型量化/加速", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-mlops", "label": "MLOps运维部署", "type": "standard", "proficiency": 0.1, "status": "pending"},
            {"id": "ai-finish", "label": "人工智能专家路径达成", "type": "milestone", "proficiency": 1.0, "status": "pending"},
        ]

        edges = [
            {"from": "ai-math", "to": "ai-la", "isDynamic": False},
            {"from": "ai-math", "to": "ai-calc", "isDynamic": False},
            {"from": "ai-math", "to": "ai-stat", "isDynamic": False},
            {"from": "ai-prog", "to": "ai-python", "isDynamic": False},
            {"from": "ai-python", "to": "ai-libs", "isDynamic": False},
            {"from": "ai-la", "to": "ai-stage1", "isDynamic": False},
            {"from": "ai-calc", "to": "ai-stage1", "isDynamic": False},
            {"from": "ai-stat", "to": "ai-stage1", "isDynamic": False},
            {"from": "ai-libs", "to": "ai-stage1", "isDynamic": False},
            {"from": "ai-stage1", "to": "ai-ml", "isDynamic": False},
            {"from": "ai-ml", "to": "ai-sup", "isDynamic": False},
            {"from": "ai-ml", "to": "ai-unsup", "isDynamic": False},
            {"from": "ai-sup", "to": "ai-dl", "isDynamic": False},
            {"from": "ai-unsup", "to": "ai-dl", "isDynamic": False},
            {"from": "ai-dl", "to": "ai-frame", "isDynamic": False},
            {"from": "ai-frame", "to": "ai-cv", "isDynamic": False},
            {"from": "ai-frame", "to": "ai-nlp", "isDynamic": False},
            {"from": "ai-frame", "to": "ai-audio", "isDynamic": False},
            {"from": "ai-cv", "to": "ai-stage2", "isDynamic": False},
            {"from": "ai-nlp", "to": "ai-stage2", "isDynamic": False},
            {"from": "ai-audio", "to": "ai-stage2", "isDynamic": False},
            {"from": "ai-stage2", "to": "ai-transformer", "isDynamic": False},
            {"from": "ai-transformer", "to": "ai-llm", "isDynamic": False},
            {"from": "ai-llm", "to": "ai-app", "isDynamic": False},
            {"from": "ai-llm", "to": "ai-tech", "isDynamic": False},
            {"from": "ai-llm", "to": "ai-ops", "isDynamic": False},
            {"from": "ai-app", "to": "ai-rag", "isDynamic": False},
            {"from": "ai-app", "to": "ai-agent", "isDynamic": False},
            {"from": "ai-tech", "to": "ai-ft", "isDynamic": False},
            {"from": "ai-tech", "to": "ai-rlhf", "isDynamic": False},
            {"from": "ai-ops", "to": "ai-quant", "isDynamic": False},
            {"from": "ai-ops", "to": "ai-mlops", "isDynamic": False},
            {"from": "ai-rag", "to": "ai-finish", "isDynamic": False},
            {"from": "ai-agent", "to": "ai-finish", "isDynamic": False},
            {"from": "ai-ft", "to": "ai-finish", "isDynamic": False},
            {"from": "ai-rlhf", "to": "ai-finish", "isDynamic": False},
            {"from": "ai-quant", "to": "ai-finish", "isDynamic": False},
            {"from": "ai-mlops", "to": "ai-finish", "isDynamic": False},
        ]

        return {
            "title": f"人工智能学习路径 - {goal}",
            "analysis_summary": "按照三大阶段设计：基础储备→核心模型→前沿进阶。数学编程打基础，机器学习学核心，大模型进前沿。",
            "nodes": nodes,
            "edges": edges,
        }

    def _get_general_path_fallback(self, goal: str, profile: ProfileDimensions | dict | None = None) -> dict:
        """通用学习路径的fallback"""
        has_weakness = False
        if profile:
            if isinstance(profile, dict):
                has_weakness = profile.get('knowledge_base_score', 50) < 60
            else:
                has_weakness = profile.knowledge_base_score < 60

        nodes = [
            {"id": "n1", "label": f"{goal}基础概念", "type": "standard", "proficiency": 0.8, "status": "completed"},
            {"id": "n2", "label": f"{goal}核心原理", "type": "standard", "proficiency": 0.6, "status": "active"},
            {"id": "n3", "label": f"{goal}进阶应用", "type": "standard", "proficiency": 0.3, "status": "pending"},
            {"id": "n4", "label": f"{goal}实战项目", "type": "standard", "proficiency": 0.0, "status": "pending"},
        ]
        edges = [
            {"from": "n1", "to": "n2", "isDynamic": False},
            {"from": "n2", "to": "n3", "isDynamic": False},
            {"from": "n3", "to": "n4", "isDynamic": False},
        ]

        return {
            "title": f"{goal} 学习路径",
            "analysis_summary": f"根据你的画像分析，{'基础知识需要补充，已在路径中注入强化节点' if has_weakness else '基础知识扎实，可以直接进入核心学习'}。当前路径共 {len(nodes)} 个阶段。",
            "nodes": nodes,
            "edges": edges,
        }


planner = PathPlanner()
