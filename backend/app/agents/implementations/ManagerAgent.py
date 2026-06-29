"""
Manager Agent - 主控中枢
负责协调整个Agent流程和任务调度
"""
import json
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils


class ManagerAgent(BaseAgent):
    """主控中枢 — 第一个执行的Agent，负责任务分解"""

    PROMPT_TEMPLATE = """
你是一个智能任务协调员，专门负责规划和管理复杂的多智能体任务。
请根据以下主题生成任务规划和协调指令：

主题: {topic}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{
  "tasks": ["子任务1", "子任务2", "子任务3", "子任务4", "子任务5", "子任务6", "子任务7"],
  "priority": ["professor", "architect", "examiner", "director", "hacker", "reviewer"],
  "coordination_notes": [
    "教授智能体应在架构师之前生成基础内容",
    "考官智能体应基于教授的内容设计题目",
    "导演智能体需要基于架构师的结构制作脚本"
  ]
}
```

任务规划要求：
- 将"生成关于 {topic} 的完整教学内容"分解为7个子任务
- 确保逻辑连贯性，明确任务边界
- 合理分配给不同的智能体
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
            if parsed:
                content = {
                    "tasks": parsed.get("tasks", [context.topic]),
                    "priority": parsed.get("priority", []),
                    "coordination_notes": parsed.get("coordination_notes", []),
                    "raw_response": llm_response,
                }
            else:
                content = {
                    "tasks": [context.topic],
                    "priority": [],
                    "coordination_notes": [llm_response.strip()],
                    "raw_response": llm_response,
                }

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
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.ERROR,
                error=str(error),
                duration=duration
            )
