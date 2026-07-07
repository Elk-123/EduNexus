"""
Architect Agent - 架构师智能体
负责生成思维导图和知识结构图（v1 兼容格式）
"""
import json
import logging
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..fallback_data import get_fallback_content

logger = logging.getLogger("edunexus.agents")


class ArchitectAgent(BaseAgent):
    """架构师智能体 — 生成知识结构/思维导图（v1 兼容格式）"""

    PROMPT_TEMPLATE = """
你是一个专业的知识架构师，专门负责将复杂主题转化为清晰的思维导图结构。

⚠️ 核心约束：你必须且只能围绕下面这个主题构建思维导图！

生成主题：{topic}

上游教授已生成的教学内容：{context}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{{
  "mindmap": {{
    "root": "【上述主题的名称】",
    "children": [
      {{"name": "一级分支（与上述主题直接相关）", "children": [{{"name": "二级分支"}}]}}
    ]
  }}
}}
```

要求：
- 根节点必须是上述生成主题的名称，不可更换
- 看到上游教授的教学内容中提到了哪些关键概念，将它们组织成思维导图
- 至少3个一级分支，每个一级分支下至少2-3个子节点
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
                # v1 兼容：确保输出包含 mindmap 顶层 key
                if "mindmap" in parsed:
                    content = parsed
                elif "root" in parsed:
                    # v2 旧格式 → 包裹为 v1 格式
                    content = {"mindmap": parsed}
                else:
                    content = parsed
            else:
                logger.warning("ArchitectAgent: LLM returned non-JSON, using fallback")
                content = get_fallback_content("architect", context.topic)

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
            logger.warning("ArchitectAgent LLM call failed: %s — using fallback", error)
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fallback_content = get_fallback_content("architect", context.topic)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=fallback_content,
                    type="mindmap",
                    timestamp=datetime.now(),
                    log=[f"使用 fallback 数据生成架构图: {context.topic}"]
                ),
                duration=duration
            )
