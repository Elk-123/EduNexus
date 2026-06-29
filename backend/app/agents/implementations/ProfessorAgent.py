"""
Professor Agent - 教授智能体
负责生成学术性的、结构化的教学内容
"""
import json
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils


class ProfessorAgent(BaseAgent):
    """教授智能体 — 生成结构化教学内容"""

    PROMPT_TEMPLATE = """
你是一个资深的教育专家，专门负责生成高质量的教学内容。
请根据以下信息生成一份结构化的学术性内容：

主题: {topic}
参考上下文（上游Agent输出）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{
  "title": "主题标题",
  "sections": [
    {"heading": "章节标题", "body": "详细内容（至少100字）"}
  ],
  "keyConcepts": [
    {"name": "概念名称", "explanation": "概念解释"}
  ]
}
```

请确保内容具有教育价值，逻辑清晰，包含至少3个章节和3个关键概念。
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
                    "title": parsed.get("title", f"关于{context.topic}的学术解析"),
                    "sections": parsed.get("sections", []),
                    "keyConcepts": parsed.get("keyConcepts", []),
                }
            else:
                content = {
                    "title": f"关于{context.topic}的学术解析",
                    "sections": [{"heading": "LLM 生成内容", "body": llm_response.strip()}],
                    "keyConcepts": [],
                }

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
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.ERROR,
                error=str(error),
                duration=duration
            )
