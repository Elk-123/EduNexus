"""
Manager Agent - 主控中枢
负责协调整个Agent流程和任务调度（v1 兼容格式）
"""
import json
import logging
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..fallback_data import get_fallback_content

logger = logging.getLogger("edunexus.agents")


class ManagerAgent(BaseAgent):
    """主控中枢 — 第一个执行的Agent，负责任务分解"""

    PROMPT_TEMPLATE = """
你是一个智能任务协调员，专门负责规划和管理复杂的多智能体教学任务。

🔴【主题锁定】当前需要生成教学内容的主题是：「{topic}」
🔴 你接下来的所有输出必须且只能围绕「{topic}」这个主题。
🔴 绝对禁止将主题替换为其他任何话题（如机器学习、编程、数学等）。
🔴 如果主题是「Transformer注意力机制」，你只能规划关于Transformer注意力机制的任务，不能换成机器学习或深度学习。

请根据这个主题，生成以下JSON格式的任务计划（严格JSON，不要包含任何其他文字）：
```json
{{
  "tasks": [
    "确定「{topic}」的教学目标和核心知识点",
    "设计「{topic}」的课程大纲与知识结构",
    "编写「{topic}」的详细教学内容与示例",
    "创建「{topic}」的评估题目和答案",
    "制作「{topic}」的教学视频脚本",
    "开发「{topic}」的互动练习与代码案例",
    "审核并优化「{topic}」的全部教学材料"
  ],
  "priority": ["professor", "architect", "examiner", "director", "hacker", "reviewer"],
  "coordination_notes": [
    "教授智能体应在架构师之前生成基础内容",
    "考官智能体应基于教授的内容设计题目",
    "导演智能体需要基于架构师的结构制作脚本"
  ]
}}
```

要求：
- tasks 数组必须有恰好7个任务，每个任务必须明确提及「{topic}」
- priority 必须严格按照 ["professor", "architect", "examiner", "director", "hacker", "reviewer"] 顺序
"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                id="manager",
                name="主控中枢",
                role="任务协调专家",
                capabilities=["任务规划", "流程协调", "资源调度"],
                timeout=30000
            )
        super().__init__(config)

    def execute(self, context: AgentContext) -> AgentExecutionResult:
        start_time = datetime.now()
        try:
            prompt_template = LangChainUtils.create_prompt_template(self.PROMPT_TEMPLATE)
            llm_response = LangChainUtils.execute_chain(prompt_template, {
                "topic": context.topic
            })

            parsed = LangChainUtils.try_parse_json(llm_response)
            if parsed and isinstance(parsed.get("tasks"), list) and len(parsed["tasks"]) >= 5:
                content = {
                    "tasks": parsed.get("tasks", []),
                    "priority": parsed.get("priority", ["professor", "architect", "examiner", "director", "hacker", "reviewer"]),
                    "coordination_notes": parsed.get("coordination_notes", []),
                }
            else:
                logger.warning("ManagerAgent: output validation failed (missing tasks), using fallback")
                content = get_fallback_content("manager", context.topic)

            self._record_success(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=content,
                    type="task_plan",
                    timestamp=datetime.now(),
                    log=[f"成功生成任务计划: {context.topic}"]
                ),
                duration=duration
            )
        except Exception as error:
            logger.warning("ManagerAgent LLM call failed: %s — using fallback", error)
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fallback_content = get_fallback_content("manager", context.topic)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=fallback_content,
                    type="task_plan",
                    timestamp=datetime.now(),
                    log=[f"使用 fallback 数据生成任务计划: {context.topic}"]
                ),
                duration=duration
            )
