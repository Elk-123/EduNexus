"""
Professor Agent - 教授智能体
负责生成学术性的、结构化的教学内容
"""
from typing import Dict, Any
from . import BaseAgent, AgentConfig, AgentContext, AgentExecutionResult, AgentResult
from ..utils.LangChainUtils import LangChainUtils

class ProfessorAgent(BaseAgent):
    """教授智能体"""

    PROMPT_TEMPLATE = """
你是一个资深的教育专家，专门负责生成高质量的教学内容。
请根据以下主题生成一份结构化的学术性内容：

主题: {topic}

你需要生成以下内容：
1. 标题：简洁明了的主题标题
2. 内容章节：至少3个章节，每个章节包含标题和详细内容
3. 关键概念：列出该主题中的3个关键概念及其解释

请确保内容具有教育价值，逻辑清晰，适合学生学习使用。
"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                id="professor",
                name="教授智能体",
                role="学术内容生成专家",
                capabilities=["结构化内容生成", "学术写作", "知识梳理"],
                timeout=30000
            )
        super().__init__(config)

    def execute(self, context: AgentContext) -> AgentExecutionResult:
        """执行任务"""
        try:
            prompt_template = LangChainUtils.create_prompt_template(self.PROMPT_TEMPLATE)
            result = LangChainUtils.execute_chain(prompt_template, {
                "topic": context.topic
            })

            return AgentExecutionResult(
                agent_id=self.config.id,
                status="success",
                result=AgentResult(
                    content={
                        "title": f"关于{context.topic}的学术解析",
                        "sections": [
                            {
                                "heading": "引言",
                                "body": f"这是一个关于{context.topic}的详细介绍。"
                            },
                            {
                                "heading": "核心概念",
                                "body": f"我们将深入探讨{context.topic}的核心要素。"
                            },
                            {
                                "heading": "应用实例",
                                "body": f"下面我们将通过实际案例来展示{context.topic}的应用。"
                            }
                        ],
                        "keyConcepts": [
                            "概念1",
                            "概念2",
                            "概念3"
                        ]
                    },
                    type="academic_content",
                    timestamp=datetime.now(),
                    log=[f"成功生成教授内容: {context.topic}"]
                ),
                duration=0
            )
        except Exception as error:
            return AgentExecutionResult(
                agent_id=self.config.id,
                status="error",
                error=str(error),
                duration=0
            )

    def get_status(self) -> "AgentStatusInfo":
        """获取状态"""
        # 实现获取状态的逻辑
        from ..types import AgentStatusInfo, AgentStatus
        return AgentStatusInfo(
            agent_id=self.config.id,
            status=AgentStatus.IDLE,
            last_updated=datetime.now(),
            success_count=0,
            failure_count=0
        )

    def interrupt(self) -> None:
        """中断执行"""
        print("Professor agent interrupted")