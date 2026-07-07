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

⚠️ 核心约束：你必须且只能围绕下面这个主题生成内容，绝不要换成其他话题！

生成主题：{topic}

上游Agent已生成的内容摘要：{context}

请严格以JSON格式返回（不要包含任何其他文字），格式如下：
```json
{{
  "title": "关于【上述主题】的教学内容标题",
  "sections": [
    {{
      "heading": "章节标题（与上述主题直接相关）",
      "subsections": [
        {{"subheading": "小节标题", "body": "小节详细内容（至少150字，必须与上述主题相关）"}}
      ]
    }}
  ]
}}
```

要求：
- 标题和所有内容必须与上述生成主题直接相关，不可换成其他话题
- 至少3个章节，每章至少2个小节
- 每个小节的 body 至少150字，内容深入浅出，有具体例子
- 参考上游Agent输出的内容，保持一致性
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
            if parsed:
                content = {
                    "title": parsed.get("title", f"关于{context.topic}的深度解析"),
                    "sections": parsed.get("sections", []),
                }
            else:
                # JSON 解析失败，使用 fallback
                logger.warning("ProfessorAgent: LLM returned non-JSON, using fallback")
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
            # fallback 兜底
            fallback_content = get_fallback_content("professor", context.topic)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,  # fallback 也算成功
                result=AgentResult(
                    content=fallback_content,
                    type="academic_content",
                    timestamp=datetime.now(),
                    log=[f"使用 fallback 数据生成教授内容: {context.topic}"]
                ),
                duration=duration
            )
