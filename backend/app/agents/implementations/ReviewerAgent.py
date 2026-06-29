"""
Reviewer Agent - 质量审查
负责审查和优化所有生成内容的质量
"""
import json
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils


class ReviewerAgent(BaseAgent):
    """质量审查 — 审查所有上游Agent的输出"""

    PROMPT_TEMPLATE = """
你是一个专业的质量审查专家，负责对教育内容进行审查和优化。
请根据以下所有生成的内容进行质量审查：

主题: {topic}

以下是所有上游Agent生成的完整内容：
{content}

请严格以JSON格式返回审查报告（不要包含任何其他文字）：
```json
{
  "hallucination_risk": "low/medium/high",
  "quality_score": 8.5,
  "suggestions": ["具体改进建议1", "具体改进建议2", "具体改进建议3"],
  "difficulty_assessment": "难度评估（如：适合初学者/中等偏难/高级）",
  "review_summary": "总体评价（100字以内）"
}
```

审查标准：
- 准确性：内容是否准确无误
- 清晰度：表达是否清晰易懂
- 完整性：是否涵盖主题的各个方面
- 教育价值：是否适合目标学习者
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
        start_time = datetime.now()
        try:
            # 将累积的所有上游Agent输出格式化传入 prompt
            content_json = json.dumps(context.context, ensure_ascii=False, indent=2) if context.context else context.topic

            prompt_template = LangChainUtils.create_prompt_template(self.PROMPT_TEMPLATE)
            llm_response = LangChainUtils.execute_chain(prompt_template, {
                "topic": context.topic,
                "content": content_json,
            })

            parsed = LangChainUtils.try_parse_json(llm_response)
            if parsed:
                content = {
                    "hallucination_risk": parsed.get("hallucination_risk", "low"),
                    "quality_score": float(parsed.get("quality_score", 7.0)),
                    "suggestions": parsed.get("suggestions", []),
                    "difficulty_assessment": parsed.get("difficulty_assessment", "中等"),
                    "review_summary": parsed.get("review_summary", ""),
                }
            else:
                content = {
                    "hallucination_risk": "low",
                    "quality_score": 7.0,
                    "suggestions": [],
                    "difficulty_assessment": "中等",
                    "review_summary": llm_response.strip()[:500],
                }

            self._record_success(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=content,
                    type="review",
                    timestamp=datetime.now(),
                    log=[f"成功完成内容审查: {context.topic}"]
                ),
                duration=duration
            )
        except Exception as error:
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.ERROR,
                error=str(error),
                duration=duration
            )
