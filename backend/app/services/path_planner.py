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

        # 将三阶段标准硬性写入 Prompt 约束
        prompt = f"""你是一位资深课程设计师和AI教育专家。
        请根据学习目标生成一个【三阶段结构化】的个性化 DAG 学习路径。

        学习目标: {goal}
        {profile_context}

        【核心设计规范】
        1. 必须将整个学习路径严格划分为三个阶段（Phase）：
           - 阶段 1 (phase=1)：基础储备（偏向概念、工具、语言或理论准备工作）
           - 阶段 2 (phase=2)：核心掌握（偏向核心原理、主体模型、专业深度技能）
           - 阶段 3 (phase=3)：前沿进阶/实战（偏向实战项目、部署、优化或前沿应用）
        2. 阶段内多路并进：每个阶段内部包含 2-3 个标准节点 (type="standard")，可以有分叉连线以体现 DAG。
        3. 里程碑衔接：每个阶段的末尾必须有且仅有一个里程碑节点 (type="milestone")。
           - 阶段内的标准节点最终必须全部指向该阶段的里程碑节点。
           - 上一个阶段的里程碑节点，必须连线指向下一个阶段的起始标准节点，从而实现阶段间的顺序演进。
        4. 薄弱领域强化：如果学生存在薄弱领域（如基础薄弱、抗压低），请在阶段1或阶段2中插入 1-2 个补充节点 (type="injected")，并规划好前置依赖。

        请输出以下 JSON，不得包含任何 Markdown 格式以外的解释性文字：
        {{
            "title": "学习路径标题",
            "analysis_summary": "基于学生画像的分析总结，指出薄弱环节和注入节点原因(100字以内)",
            "nodes": [
                {{
                    "id": "p1-node-1", 
                    "label": "知识点名称", 
                    "type": "standard", 
                    "phase": 1, 
                    "proficiency": 0.8, 
                    "status": "completed"
                }},
                {{
                    "id": "p1-milestone", 
                    "label": "第一阶段：基础储备完成", 
                    "type": "milestone", 
                    "phase": 1, 
                    "proficiency": 1.0, 
                    "status": "pending"
                }},
                ...
            ],
            "edges": [
                {{"from": "p1-node-1", "to": "p1-milestone", "isDynamic": false}},
                {{"from": "p1-milestone", "to": "p2-node-1", "isDynamic": false}},
                ...
            ]
        }}

        要求:
        - 总节点数控制在 8-12 个（包含 standard, milestone 和可能存在的 injected 节点）。
        - 确保整个图是一个有向无环图（DAG），不可出现闭环。
        - 每个节点的 proficiency 值基于学生画像进行合理估算。
        - 状态分配规则：阶段1的起始节点为 "completed"，阶段1的其他节点和阶段2的起始节点为 "active"，后续节点为 "pending"。
        """

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位资深课程设计师和AI教育专家。请严格按照JSON格式输出结构化的三阶段学习路径。确保没有环路。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4, # 适当降低 temperature 以保证结构化输出的稳定性
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
        """人工智能学习路径的fallback - 三个阶段设计 (已补充 phase 字段以便前端统一处理)"""
        nodes = [
            {"id": "ai-math", "label": "数学基础", "type": "standard", "phase": 1, "proficiency": 0.8, "status": "completed"},
            {"id": "ai-prog", "label": "编程开发", "type": "standard", "phase": 1, "proficiency": 0.8, "status": "completed"},
            {"id": "ai-la", "label": "线性代数", "type": "standard", "phase": 1, "proficiency": 0.7, "status": "active"},
            {"id": "ai-calc", "label": "微积分", "type": "standard", "phase": 1, "proficiency": 0.7, "status": "active"},
            {"id": "ai-stat", "label": "概率统计", "type": "standard", "phase": 1, "proficiency": 0.7, "status": "active"},
            {"id": "ai-python", "label": "Python核心语法", "type": "standard", "phase": 1, "proficiency": 0.8, "status": "active"},
            {"id": "ai-libs", "label": "数据处理库", "type": "standard", "phase": 1, "proficiency": 0.6, "status": "pending"},
            {"id": "ai-stage1", "label": "第一阶段：基础储备完成", "type": "milestone", "phase": 1, "proficiency": 1.0, "status": "pending"},
            
            {"id": "ai-ml", "label": "经典机器学习", "type": "standard", "phase": 2, "proficiency": 0.4, "status": "pending"},
            {"id": "ai-sup", "label": "监督学习", "type": "standard", "phase": 2, "proficiency": 0.4, "status": "pending"},
            {"id": "ai-unsup", "label": "无监督学习", "type": "standard", "phase": 2, "proficiency": 0.4, "status": "pending"},
            {"id": "ai-dl", "label": "深度学习基础", "type": "standard", "phase": 2, "proficiency": 0.3, "status": "pending"},
            {"id": "ai-frame", "label": "深度学习框架", "type": "standard", "phase": 2, "proficiency": 0.3, "status": "pending"},
            {"id": "ai-cv", "label": "计算机视觉", "type": "standard", "phase": 2, "proficiency": 0.2, "status": "pending"},
            {"id": "ai-nlp", "label": "自然语言处理", "type": "standard", "phase": 2, "proficiency": 0.2, "status": "pending"},
            {"id": "ai-audio", "label": "语音信号处理", "type": "standard", "phase": 2, "proficiency": 0.2, "status": "pending"},
            {"id": "ai-stage2", "label": "第二阶段：核心模型掌握", "type": "milestone", "phase": 2, "proficiency": 1.0, "status": "pending"},
            
            {"id": "ai-transformer", "label": "Transformer架构", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-llm", "label": "大语言模型原理", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-app", "label": "应用开发层", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-tech", "label": "模型调优层", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-ops", "label": "工程部署层", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-rag", "label": "RAG检索增强", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-agent", "label": "AI智能体", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-ft", "label": "LoRA/PEFT微调", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-rlhf", "label": "强化学习对齐", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-quant", "label": "模型量化/加速", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-mlops", "label": "MLOps运维部署", "type": "standard", "phase": 3, "proficiency": 0.1, "status": "pending"},
            {"id": "ai-finish", "label": "人工智能专家路径达成", "type": "milestone", "phase": 3, "proficiency": 1.0, "status": "pending"},
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
        """通用学习路径的fallback (已补充 phase 字段)"""
        has_weakness = False
        if profile:
            if isinstance(profile, dict):
                has_weakness = profile.get('knowledge_base_score', 50) < 60
            else:
                has_weakness = profile.knowledge_base_score < 60

        nodes = [
            {"id": "n1", "label": f"{goal}基础概念", "type": "standard", "phase": 1, "proficiency": 0.8, "status": "completed"},
            {"id": "n2", "label": f"{goal}核心原理", "type": "standard", "phase": 2, "proficiency": 0.6, "status": "active"},
            {"id": "n3", "label": f"{goal}进阶应用", "type": "standard", "phase": 3, "proficiency": 0.3, "status": "pending"},
            {"id": "n4", "label": f"{goal}实战项目", "type": "standard", "phase": 3, "proficiency": 0.0, "status": "pending"},
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