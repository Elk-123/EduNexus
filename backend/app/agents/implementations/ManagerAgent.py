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

当前需要生成教学内容的主题是：{topic}

请根据这个主题，生成以下JSON格式的任务计划（不要包含任何其他文字）：
```json
{{
  "tasks": [
    "任务1描述",
    "任务2描述",
    "任务3描述",
    "任务4描述",
    "任务5描述",
    "任务6描述",
    "任务7描述"
  ],
  "priority": ["professor", "architect", "examiner", "director", "hacker", "reviewer"],
  "coordination_notes": [
    "协调说明1",
    "协调说明2",
    "协调说明3"
  ]
}}
```

要求：
- tasks 中的每个任务必须明确提及上述主题，例如"确定【具体主题】的教学目标"
- 将生成完整教学内容分解为7个子任务
- 确保逻辑连贯，任务边界清晰
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
                    "tasks": parsed.get("tasks", [
                        f"确定「{context.topic}」的教学目标和核心知识点",
                        f"设计「{context.topic}」的课程大纲与知识结构",
                        f"编写「{context.topic}」的详细教学内容与示例",
                        f"创建「{context.topic}」的评估题目和答案",
                        f"制作「{context.topic}」的教学视频脚本",
                        f"开发「{context.topic}」的互动练习与代码案例",
                        f"审核并优化「{context.topic}」的全部教学材料",
                    ]),
                    "priority": parsed.get("priority", ["professor", "architect", "examiner", "director", "hacker", "reviewer"]),
                    "coordination_notes": parsed.get("coordination_notes", [
                        "教授智能体应在架构师之前生成基础内容",
                        "考官智能体应基于教授的内容设计题目",
                        "导演智能体需要基于架构师的结构制作脚本",
                    ]),
                }
            else:
                logger.warning("ManagerAgent: LLM returned non-JSON, using fallback")
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
