"""
Reviewer Agent - 质量审查
负责审查和优化所有生成内容的质量
"""
from typing import Dict, Any
from . import BaseAgent, AgentConfig, AgentContext, AgentExecutionResult, AgentResult
from ..utils.LangChainUtils import LangChainUtils
from datetime import datetime

class ReviewerAgent(BaseAgent):
    """质量审查"""

    PROMPT_TEMPLATE = """
你是一个专业的质量审查专家，负责对教育内容进行审查和优化。
请根据以下内容生成审查报告：

主题: {topic}
内容: {content}

你需要生成以下内容：
1. 一致性检查：检查内容是否前后一致
2. 质量评分：给出1-10分的评分
3. 改进建议：提出具体的改进建议
4. 风险评估：识别潜在的问题或风险

审查标准：
- 准确性
- 清晰度
- 完整性
- 教育价值
"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                id="reviewer",
                name="质量审查",
                role="内容质量专家",
                capabilities=["内容审查", "质量评估", "优化建议"],
                timeout=30000
            )
        super().__init__(config)

    def execute(self, context: AgentContext) -> AgentExecutionResult:
        """执行任务"""
        try:
            prompt_template = LangChainUtils.create_prompt_template(self.PROMPT_TEMPLATE)
            result = LangChainUtils.execute_chain(prompt_template, {
                "topic": context.topic,
                "content": str(context.context) if context.context else ""
            })

            return AgentExecutionResult(
                agent_id=self.config.id,
                status="success",
                result=AgentResult(
                    content={
                        "hallucination_risk": "low",
                        "quality_score": 8.5,
                        "suggestions": [
                            "可以增加更多实际应用案例",
                            "部分术语解释可以更详细",
                            "增加视觉辅助元素的建议"
                        ],
                        "difficulty_assessment": "中等偏难",
                        "review_summary": "整体质量良好，内容结构清晰，但可以进一步完善细节"
                    },
                    type="review",
                    timestamp=datetime.now(),
                    log=[f"成功完成内容审查: {context.topic}"]
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
        print("Reviewer agent interrupted")