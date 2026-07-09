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

🔴【主题锁定】生成主题：「{topic}」
🔴 你接下来的思维导图必须且只能围绕「{topic}」构建。
🔴 根节点必须是「{topic}」本身或其核心概念，绝对不可以换成其他主题。
🔴 如果主题是「Transformer注意力机制」，根节点必须是关于注意力机制的，一级分支必须是QKV、多头注意力、缩放点积等。

上游教授已生成的教学内容：{context}

请严格以JSON格式返回（不要包含任何其他文字，不要markdown代码块标记）：
{{
  "mindmap": {{
    "root": "root(({topic}))",
    "children": [
      {{"name": "一级分支（与{topic}直接相关）", "children": [{{"name": "二级分支"}}, {{"name": "二级分支"}}]}},
      {{"name": "一级分支", "children": [{{"name": "二级分支"}}, {{"name": "二级分支"}}]}},
      {{"name": "一级分支", "children": [{{"name": "二级分支"}}, {{"name": "二级分支"}}]}}
    ]
  }}
}}

要求：
- mindmap.root 必须包含「{topic}」
- 至少3个一级分支，每个一级分支下至少2个子节点
- 看到上游教授的教学内容中提到了哪些关键概念，将它们组织成思维导图
- 节点名使用中文，简洁明了（10字以内）
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
            # ★ 关键修复：严格验证 mindmap 结构
            content = None
            if parsed:
                if "mindmap" in parsed and isinstance(parsed["mindmap"], dict):
                    mm = parsed["mindmap"]
                    if isinstance(mm.get("root"), str) and isinstance(mm.get("children"), list) and len(mm["children"]) > 0:
                        content = parsed  # 结构完整，通过
                    else:
                        logger.warning("ArchitectAgent: mindmap missing root or children, using fallback")
                elif "root" in parsed and isinstance(parsed.get("children"), list):
                    # v2 旧格式：直接是 {root, children} → 包裹为 mindmap
                    if len(parsed["children"]) > 0:
                        content = {"mindmap": parsed}
                    else:
                        logger.warning("ArchitectAgent: root format but empty children, using fallback")
                else:
                    logger.warning("ArchitectAgent: parsed JSON lacks mindmap/root structure, using fallback")

            if content is None:
                logger.warning("ArchitectAgent: output validation failed, using fallback")
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
