"""
Agent模块主入口
导出所有Agent相关功能
"""

# 基础类
from .base.BaseAgent import BaseAgent

# 协调器
from .coordinator.AgentCoordinator import AgentCoordinator

# 工具类
from .utils.LangChainUtils import LangChainUtils

# 具体Agent实现
from .implementations.ManagerAgent import ManagerAgent
from .implementations.ProfessorAgent import ProfessorAgent
from .implementations.ArchitectAgent import ArchitectAgent
from .implementations.ExaminerAgent import ExaminerAgent
from .implementations.DirectorAgent import DirectorAgent
from .implementations.HackerAgent import HackerAgent
from .implementations.ReviewerAgent import ReviewerAgent

# 类型定义
from .types import (
    AgentConfig, AgentContext, AgentResult, AgentExecutionResult, AgentStatusInfo,
    AgentStatus, AgentType
)

__all__ = [
    # 基础类
    'BaseAgent',

    # 协调器
    'AgentCoordinator',

    # 工具类
    'LangChainUtils',

    # 具体Agent
    'ManagerAgent',
    'ProfessorAgent',
    'ArchitectAgent',
    'ExaminerAgent',
    'DirectorAgent',
    'HackerAgent',
    'ReviewerAgent',

    # 类型定义
    'AgentConfig',
    'AgentContext',
    'AgentResult',
    'AgentExecutionResult',
    'AgentStatusInfo',
    'AgentStatus',
    'AgentType'
]