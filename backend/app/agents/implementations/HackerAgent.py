"""
Hacker Agent - 极客智能体
负责生成代码示例和编程练习
"""
from typing import Dict, Any
from . import BaseAgent, AgentConfig, AgentContext, AgentExecutionResult, AgentResult
from ..utils.LangChainUtils import LangChainUtils
from datetime import datetime

class HackerAgent(BaseAgent):
    """极客智能体"""

    PROMPT_TEMPLATE = """
你是一个经验丰富的程序员和教育专家，专门负责生成编程相关的教学内容。
请根据以下主题生成一套编程教学材料：

主题: {topic}

你需要生成以下内容：
1. 代码示例：一个完整的可运行代码片段
2. 代码说明：详细解释代码的功能和实现方式
3. 练习题目：2个编程练习题，包含要求和参考答案

代码要求：
- 代码应该清晰、简洁、易懂
- 包含必要的注释
- 符合最佳实践
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
                        "title": f"{context.topic} 编程示例",
                        "description": f"这是一个关于{context.topic}的完整代码示例",
                        "code": f"// {context.topic} 示例代码\nfunction exampleFunction() {\n  // 实现{context.topic}的核心功能\n  console.log(\"Hello from {context.topic}\");\n  return true;\n}",
                        "expected_output": "Hello from Transformer Architecture",
                        "exercises": [
                            {
                                "title": "基础练习",
                                "description": "根据提供的代码实现一个类似功能",
                                "requirement": "实现一个接受参数的函数",
                                "hint": "参考示例代码的结构"
                            },
                            {
                                "title": "进阶练习",
                                "description": "扩展功能以满足额外要求",
                                "requirement": "添加错误处理机制",
                                "hint": "考虑使用try-catch语句"
                            }
                        ]
                    },
                    type="code",
                    timestamp=datetime.now(),
                    log=[f"成功生成代码内容: {context.topic}"]
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
        print("Hacker agent interrupted")