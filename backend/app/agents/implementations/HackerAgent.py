"""
Hacker Agent - 极客智能体
负责生成代码示例和编程练习
"""
import json
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils


class HackerAgent(BaseAgent):
    """极客智能体 — 生成代码示例与编程练习"""

    PROMPT_TEMPLATE = """
你是一个经验丰富的程序员和教育专家，专门负责生成编程相关的教学内容。
请根据以下信息生成一套编程教学材料：

主题: {topic}
参考上下文（上游Agent输出的教学内容）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{
  "title": "代码示例标题",
  "description": "代码功能描述",
  "code": "完整的可运行代码（包含注释）",
  "expected_output": "预期输出结果",
  "exercises": [
    {
      "title": "练习标题",
      "description": "练习描述",
      "requirement": "练习要求",
      "hint": "提示"
    }
  ]
}
```

要求：代码清晰简洁，包含必要注释，提供至少2个练习题。
"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                id="hacker",
                name="极客智能体",
                role="编程教育专家",
                capabilities=["代码生成", "编程教学", "实践练习"],
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
                    "title": parsed.get("title", f"{context.topic} 编程示例"),
                    "description": parsed.get("description", ""),
                    "code": parsed.get("code", ""),
                    "expected_output": parsed.get("expected_output", ""),
                    "exercises": parsed.get("exercises", []),
                }
            else:
                content = {
                    "title": f"{context.topic} 编程示例",
                    "description": "LLM 生成的代码内容",
                    "code": llm_response.strip(),
                    "expected_output": "",
                    "exercises": [],
                }

            self._record_success(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=content,
                    type="code",
                    timestamp=datetime.now(),
                    log=[f"成功生成代码内容: {context.topic}"]
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
