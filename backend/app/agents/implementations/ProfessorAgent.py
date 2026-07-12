"""
Professor Agent - 教授智能体
负责生成学术性的、结构化的教学内容（v1 兼容格式）
"""
import json
import logging
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..fallback_data import get_fallback_content

logger = logging.getLogger("edunexus.agents")


class ProfessorAgent(BaseAgent):
    """教授智能体 — 生成结构化教学内容（v1 兼容格式）"""

    PROMPT_TEMPLATE = """
你是一个资深的教育专家，专门负责生成高质量的教学内容。

🔴【主题锁定】生成主题：「{topic}」
🔴 你接下来的所有输出必须且只能围绕「{topic}」展开。
🔴 绝对禁止将主题替换为其他话题。即使你认为其他话题更合适，也必须围绕「{topic}」。
🔴 标题、章节标题、小节内容都必须直接提及「{topic}」及其相关概念。
🔴 例如：如果主题是「Transformer注意力机制」，你的所有内容必须关于注意力机制，不能变成机器学习概述或深度学习入门。

上游Agent已生成的内容摘要：{context}

请严格以JSON格式返回（不要包含任何其他文字，不要markdown代码块标记）：
{{
  "title": "【必须包含「{topic}」关键词】的标题",
  "sections": [
    {{
      "heading": "与「{topic}」直接相关的章节标题",
      "subsections": [
        {{
        "subheading": "小节标题", 
        "body": "小节详细内容（至少150字，必须与「{topic}」直接相关）"
        }}
      ]
    }}
  ]
}}

要求：
- title 必须包含「{topic}」关键词
- 至少3个章节，每章至少2个小节
- 每个小节的 body 至少150字，内容深入浅出，有具体例子
- 所有内容必须与「{topic}」直接相关，不可偏离
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
        start_time = datetime.now()
        try:
            prompt_template = LangChainUtils.create_prompt_template(self.PROMPT_TEMPLATE)
            llm_response = LangChainUtils.execute_chain(prompt_template, {
                "topic": context.topic,
                "context": json.dumps(context.context or {}, ensure_ascii=False, indent=2),
            })

            parsed = LangChainUtils.try_parse_json(llm_response)
            # 结构验证：必须包含 title 和 sections（且 sections 是非空数组）
            if parsed and isinstance(parsed.get("title"), str) and isinstance(parsed.get("sections"), list) and len(parsed["sections"]) > 0:
                # 验证 topic 关键词是否出现在 title 中（宽松检查）
                title_ok = any(kw in parsed["title"] for kw in context.topic.split() if len(kw) >= 2)
                if not title_ok:
                    logger.warning("ProfessorAgent: title doesn't contain topic keywords, using fallback")
                    content = get_fallback_content("professor", context.topic)
                else:
                    content = {
                        "title": parsed["title"],
                        "sections": parsed["sections"],
                    }
            else:
                logger.warning("ProfessorAgent: output validation failed (missing title/sections), using fallback")
                content = get_fallback_content("professor", context.topic)

            self._record_success(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=content,
                    type="academic_content",
                    timestamp=datetime.now(),
                    log=[f"成功生成教授内容: {context.topic}"]
                ),
                duration=duration
            )
        except Exception as error:
            logger.warning("ProfessorAgent LLM call failed: %s — using fallback", error)
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fallback_content = get_fallback_content("professor", context.topic)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=fallback_content,
                    type="academic_content",
                    timestamp=datetime.now(),
                    log=[f"使用 fallback 数据生成教授内容: {context.topic}"]
                ),
                duration=duration
            )
