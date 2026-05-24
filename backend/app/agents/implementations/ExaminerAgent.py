"""
Examiner Agent - 考官智能体
负责生成测验题目和评估材料
"""
from typing import Dict, Any
from . import BaseAgent, AgentConfig, AgentContext, AgentExecutionResult, AgentResult
from ..utils.LangChainUtils import LangChainUtils
from datetime import datetime

class ExaminerAgent(BaseAgent):
    """考官智能体"""

    PROMPT_TEMPLATE = """
你是一个经验丰富的教育评估专家，专门负责设计高质量的测验题目。
请根据以下主题生成一套评估材料：

主题: {topic}

你需要生成以下内容：
1. 选择题：3道题目，每道题包含4个选项和正确答案
2. 简答题：2道开放性问题

题目要求：
- 选择题难度适中，涵盖核心知识点
- 简答题需要考察学生的理解深度
- 题目表述清晰，无歧义
"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                id="examiner",
                name="考官智能体",
                role="试题设计专家",
                capabilities=["题库生成", "评估设计", "测试策划"],
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
                        "questions": [
                            {
                                "question": f"关于{context.topic}的基础问题",
                                "options": ["选项A", "选项B", "选项C", "选项D"],
                                "answer": "选项B",
                                "explanation": "这是关于基础概念的题目"
                            },
                            {
                                "question": f"关于{context.topic}的进阶问题",
                                "options": ["选项A", "选项B", "选项C", "选项D"],
                                "answer": "选项C",
                                "explanation": "这是需要综合理解的问题"
                            },
                            {
                                "question": f"关于{context.topic}的高级问题",
                                "options": ["选项A", "选项B", "选项C", "选项D"],
                                "answer": "选项A",
                                "explanation": "这是考验应用能力的问题"
                            }
                        ],
                        "essayQuestions": [
                            {
                                "question": f"请阐述{context.topic}的核心思想",
                                "maxPoints": 10
                            },
                            {
                                "question": f"结合实例说明{context.topic}的应用",
                                "maxPoints": 15
                            }
                        ]
                    },
                    type="quiz",
                    timestamp=datetime.now(),
                    log=[f"成功生成测验材料: {context.topic}"]
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
        print("Examiner agent interrupted")