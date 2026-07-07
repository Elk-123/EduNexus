"""
Reviewer Agent - 质量审查
负责审查和优化所有生成内容的质量（v1 兼容格式）
"""
import json
import logging
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..fallback_data import get_fallback_content

logger = logging.getLogger("edunexus.agents")


class ReviewerAgent(BaseAgent):
    """质量审查 — 审查所有上游Agent的输出（v1 兼容格式）"""

    PROMPT_TEMPLATE = """
你是一个专业的教育内容质量审查专家，负责对生成的教学内容进行全面评估。

主题: {topic}

以下是所有上游Agent生成的完整内容：
{content}

请严格以JSON格式返回审查报告（不要包含任何其他文字），格式如下：
```json
{{
  "hallucination_risk": "low",
  "quality_score": 85,
  "suggestions": [
    "具体改进建议1（针对教授内容的不足之处）",
    "具体改进建议2（针对题目设计的优化方向）",
    "具体改进建议3（针对代码或脚本的补充意见）"
  ],
  "difficulty_assessment": "内容难度适中，适合有一定基础的学习者。"
}}
```

审查标准：
- 准确性：内容是否准确无误，是否有事实性错误
- 清晰度：表达是否清晰易懂
- 完整性：是否涵盖主题的各个方面
- 教育价值：是否适合目标学习者
- hallucination_risk: low（无明显幻觉）/ medium（部分存疑）/ high（多处不确定）
- quality_score: 0-100 的整数评分（100为满分，不是0-10分制！）
- suggestions: 2-4条具体可操作的改进建议
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
            content_json = json.dumps(context.context, ensure_ascii=False, indent=2) if context.context else context.topic

            prompt_template = LangChainUtils.create_prompt_template(self.PROMPT_TEMPLATE)
            llm_response = LangChainUtils.execute_chain(prompt_template, {
                "topic": context.topic,
                "content": content_json,
            })

            parsed = LangChainUtils.try_parse_json(llm_response)
            if parsed:
                # 规范化 quality_score
                qs = parsed.get("quality_score", 85)
                try:
                    quality_score = int(float(qs))
                except (ValueError, TypeError):
                    quality_score = 85

                content = {
                    "hallucination_risk": parsed.get("hallucination_risk", "low"),
                    "quality_score": quality_score,
                    "suggestions": parsed.get("suggestions", []),
                    "difficulty_assessment": parsed.get("difficulty_assessment", "中等"),
                }
            else:
                logger.warning("ReviewerAgent: LLM returned non-JSON, using fallback")
                content = get_fallback_content("reviewer", context.topic)

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
            logger.warning("ReviewerAgent LLM call failed: %s — using fallback", error)
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fallback_content = get_fallback_content("reviewer", context.topic)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=fallback_content,
                    type="review",
                    timestamp=datetime.now(),
                    log=[f"使用 fallback 数据完成审查: {context.topic}"]
                ),
                duration=duration
            )
