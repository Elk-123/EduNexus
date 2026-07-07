"""
Hacker Agent - 极客智能体
负责生成代码示例和编程练习（v1 兼容格式）
"""
import json
import logging
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..fallback_data import get_fallback_content

logger = logging.getLogger("edunexus.agents")


class HackerAgent(BaseAgent):
    """极客智能体 — 生成代码示例与编程练习（v1 兼容格式）"""

    PROMPT_TEMPLATE = """
你是一个经验丰富的程序员和教育专家，专门负责生成编程相关的教学内容。

⚠️ 核心约束：你必须且只能围绕下面这个主题编写代码！

生成主题：{topic}

上游已生成的教学内容：{context}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{{
  "title": "代码示例标题（必须包含上述主题关键词）",
  "description": "代码功能描述（50-100字）",
  "code": "完整的可运行Python代码（含详细注释，至少30行）",
  "expected_output": "运行这段代码后的预期输出结果",
  "exercises": [
    "练习1描述（与上述主题直接相关）",
    "练习2描述（与上述主题直接相关）",
    "练习3描述（与上述主题直接相关）"
  ]
}}
```

要求：
- 代码主题必须与上述生成主题一致，不可换成其他领域
- 代码完整可运行，包含 import 和详细注释
- exercises 是字符串数组（每个练习是一句话描述），至少2个
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
                # v1 兼容：确保 exercises 是字符串数组
                exercises = parsed.get("exercises", [])
                normalized_exercises = []
                for ex in exercises:
                    if isinstance(ex, str):
                        normalized_exercises.append(ex)
                    elif isinstance(ex, dict):
                        # 对象格式 → 拼接为字符串
                        parts = []
                        if ex.get("title"):
                            parts.append(ex["title"])
                        if ex.get("description"):
                            parts.append(ex["description"])
                        if ex.get("requirement"):
                            parts.append(f"要求: {ex['requirement']}")
                        normalized_exercises.append(" — ".join(parts) if parts else str(ex))
                    else:
                        normalized_exercises.append(str(ex))

                content = {
                    "title": parsed.get("title", f"{context.topic} 编程示例"),
                    "description": parsed.get("description", ""),
                    "code": parsed.get("code", ""),
                    "expected_output": parsed.get("expected_output", ""),
                    "exercises": normalized_exercises if normalized_exercises else [
                        f"修改代码中的参数，观察{context.topic}的行为变化",
                        f"尝试用另一种算法实现{context.topic}的相同功能",
                    ],
                }
            else:
                logger.warning("HackerAgent: LLM returned non-JSON, using fallback")
                content = get_fallback_content("hacker", context.topic)

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
            logger.warning("HackerAgent LLM call failed: %s — using fallback", error)
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fallback_content = get_fallback_content("hacker", context.topic)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=fallback_content,
                    type="code",
                    timestamp=datetime.now(),
                    log=[f"使用 fallback 数据生成代码: {context.topic}"]
                ),
                duration=duration
            )
