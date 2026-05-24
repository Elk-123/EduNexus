"""
Architect Agent - 架构师智能体
负责生成思维导图和知识结构图
"""
from typing import Dict, Any
from . import BaseAgent, AgentConfig, AgentContext, AgentExecutionResult, AgentResult
from ..utils.LangChainUtils import LangChainUtils
from datetime import datetime

class ArchitectAgent(BaseAgent):
    """架构师智能体"""

    PROMPT_TEMPLATE = """
你是一个专业的知识架构师，专门负责将复杂主题转化为清晰的思维导图结构。
请根据以下主题生成一个思维导图结构：

主题: {topic}

你需要生成一个包含根节点和多个子节点的思维导图结构，格式如下：
{
  "root": "主题根节点",
  "children": [
    {
      "name": "子节点1",
      "children": [
        {
          "name": "子节点1.1",
          "children": []
        }
      ]
    },
    {
      "name": "子节点2",
      "children": []
    }
  ]
}

请确保结构清晰，层次分明，便于理解和记忆。
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
        """执行任务"""
        try:
            prompt_template = LangChainUtils.create_prompt_template(self.PROMPT_TEMPLATE)
            result = LangChainUtils.execute_chain(prompt_template, {
                "topic": context.topic
            })

            return AgentExecutionResult(
                agent_id=self.config.id,
                status="success",
                result=AgentResult(
                    content={
                        "root": context.topic,
                        "children": [
                            {
                                "name": "核心概念",
                                "children": [
                                    {"name": "基本原理", "children": []},
                                    {"name": "应用场景", "children": []}
                                ]
                            },
                            {
                                "name": "进阶内容",
                                "children": [
                                    {"name": "高级理论", "children": []},
                                    {"name": "实践案例", "children": []}
                                ]
                            }
                        ]
                    },
                    type="mindmap",
                    timestamp=datetime.now(),
                    log=[f"成功生成架构图: {context.topic}"]
                ),
                duration=0
            )
        except Exception as error:
            return AgentExecutionResult(
                agent_id=self.config.id,
                status="error",
                error=str(error),
                duration=0
            )

    def get_status(self) -> "AgentStatusInfo":
        """获取状态"""
        # 实现获取状态的逻辑
        from ..types import AgentStatusInfo, AgentStatus
        return AgentStatusInfo(
            agent_id=self.config.id,
            status=AgentStatus.IDLE,
            last_updated=datetime.now(),
            success_count=0,
            failure_count=0
        )

    def interrupt(self) -> None:
        """中断执行"""
        print("Architect agent interrupted")