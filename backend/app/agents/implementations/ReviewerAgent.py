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
你是一个专业的教育内容质量审查专家。你的唯一任务是：审查关于「{topic}」的教学内容质量。

🔴🔴🔴 致命规则：你的审查报告必须100%围绕「{topic}」。每一条建议都必须明确提及「{topic}」。🔴🔴🔴

以下是所有上游Agent为「{topic}」生成的完整内容：
{content}

请严格以JSON格式返回审查报告（不要包含任何其他文字，不要markdown代码块标记）：
{{
  "hallucination_risk": "low",
  "quality_score": 85,
  "suggestions": [
    "针对「{topic}」教授内容的改进建议（必须包含{topic}关键词）",
    "针对「{topic}」题目设计的优化方向（必须包含{topic}关键词）",
    "针对「{topic}」代码或脚本的补充意见（必须包含{topic}关键词）"
  ],
  "difficulty_assessment": "针对「{topic}」学习内容的难度评估，说明适合什么水平的学习者"
}}

审查标准（每一项都必须结合「{topic}」来评估）：
- 准确性：关于「{topic}」的内容是否有事实性错误
- 清晰度：关于「{topic}」的表达是否清晰易懂
- 完整性：是否涵盖了「{topic}」的各个方面
- 教育价值：对学习「{topic}」的学习者是否有帮助
- hallucination_risk: "low" / "medium" / "high"
- quality_score: 0-100 的整数评分
- suggestions: 2-4条建议，每条必须以「{topic}」开头或直接提及「{topic}」

⚠️ 禁止：写与「{topic}」无关的通用建议（如"增加实例"、"优化结构"这种万能废话）。
⚠️ 每条建议必须具体到「{topic}」的某个知识点或某个生成内容的不足之处。
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
            # 验证：suggestions 非空，且至少一条包含 topic 关键词
            suggestions = parsed.get("suggestions", []) if parsed else []
            has_topic_in_suggestions = any(
                any(kw in s for kw in context.topic.split() if len(kw) >= 2)
                for s in suggestions
            ) if suggestions else False

            if parsed and isinstance(suggestions, list) and len(suggestions) > 0 and has_topic_in_suggestions:
                qs = parsed.get("quality_score", 85)
                try:
                    quality_score = int(float(qs))
                except (ValueError, TypeError):
                    quality_score = 85

                content = {
                    "hallucination_risk": parsed.get("hallucination_risk", "low"),
                    "quality_score": quality_score,
                    "suggestions": suggestions,
                    "difficulty_assessment": parsed.get("difficulty_assessment", "中等"),
                }
            else:
                logger.warning("ReviewerAgent: output validation failed (suggestions missing or unrelated to topic), using fallback")
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
