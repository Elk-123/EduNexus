"""
Architect Agent - 架构师智能体
负责生成思维导图和知识结构图
"""
import json
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils


class ArchitectAgent(BaseAgent):
    """架构师智能体 — 生成知识结构/思维导图"""

    PROMPT_TEMPLATE = """
你是一个专业的知识架构师，专门负责将复杂主题转化为清晰的思维导图结构。
请根据以下信息生成一个思维导图结构：

主题: {topic}
参考上下文（上游Agent输出）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{
  "root": "主题根节点",
  "children": [
    {
      "name": "一级分支1",
      "children": [
        {"name": "二级分支1.1", "children": []},
        {"name": "二级分支1.2", "children": []}
      ]
    },
    {
      "name": "一级分支2",
      "children": []
    }
  ]
}
```

请确保结构清晰，层次分明（至少2层深度），便于理解和记忆。
"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                id="architect",
                name="架构师智能体",
                role="知识结构设计师",
                capabilities=["思维导图生成", "知识架构", "可视化表达"],
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
                    "root": parsed.get("root", context.topic),
                    "children": parsed.get("children", []),
                }
            else:
                content = {
                    "root": context.topic,
                    "children": [
                        {"name": "LLM 生成内容", "children": [
                            {"name": llm_response.strip()[:100], "children": []}
                        ]}
                    ],
                }

            self._record_success(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=content,
                    type="mindmap",
                    timestamp=datetime.now(),
                    log=[f"成功生成架构图: {context.topic}"]
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
