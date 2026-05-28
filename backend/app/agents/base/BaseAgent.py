"""
Agent基类抽象定义
"""
from abc import ABC, abstractmethod
from . import AgentConfig, AgentContext, AgentExecutionResult, AgentStatusInfo

class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.system_prompt = self._build_system_prompt()
        self.system_prompt = self._build_system_prompt()
        self.system_prompt = self._build_system_prompt()

    def get_config(self) -> AgentConfig:
        """获取Agent配置"""
        return self.config

    @abstractmethod
    def execute(self, context: AgentContext) -> AgentExecutionResult:
        """执行Agent任务"""
        pass

    @abstractmethod
    def get_status(self) -> AgentStatusInfo:
        """获取Agent状态"""
        pass

    @abstractmethod
    def interrupt(self) -> None:
    def _build_system_prompt(self) -> str:
        return (
            f"You are a {self.config.agent_type} agent. ",
            "ALWAYS output thought process in <thought> tags BEFORE any tool call or final answer.\n",
            "Example: <thought>Need to search for academic papers on {topic}</thought>"
        )