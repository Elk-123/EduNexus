"""
Agent基类抽象定义
"""
from abc import ABC, abstractmethod
from . import AgentConfig, AgentContext, AgentExecutionResult, AgentStatusInfo

class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self, config: AgentConfig):
        self.config = config

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
        """中断Agent执行"""
        pass