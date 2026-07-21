"""
Agent模块主入口 — 导出所有Agent相关功能

注意: LangChainUtils 依赖 langchain_openai 包，仅在调用 initialize_model() 时才需要。
"""

# 基础类
from .base.BaseAgent import BaseAgent

# 协调器
from .coordinator.AgentCoordinator import AgentCoordinator

# 具体Agent实现
from .implementations.ManagerAgent import ManagerAgent
from .implementations.ProfessorAgent import ProfessorAgent
from .implementations.ArchitectAgent import ArchitectAgent
from .implementations.ExaminerAgent import ExaminerAgent
from .implementations.DirectorAgent import DirectorAgent
from .implementations.HackerAgent import HackerAgent
from .implementations.ReviewerAgent import ReviewerAgent

# 工具集
# [已注释] AcademicSearchTool, AcademicSearchResult, ToolRegistry — 预留 Phase 1 Tool Use
# from .tools.academic_search import AcademicSearchTool, AcademicSearchResult
# from .tools.tool_registry import ToolRegistry
from .tools.markdown_generator import MarkdownGeneratorTool  # ← 被 agent_orchestrator.py / factory.py 实际使用

# 类型定义
from .types import (
    AgentConfig, AgentContext, AgentResult, AgentExecutionResult, AgentStatusInfo,
    AgentStatus, AgentType
)

# LangChainUtils 延迟导入（需要 langchain_openai 包）
try:
    from .utils.LangChainUtils import LangChainUtils
except ImportError:
    LangChainUtils = None  # type: ignore

__all__ = [
    # 基础类
    "BaseAgent",

    # 协调器
    "AgentCoordinator",

    # 工具类
    "LangChainUtils",

    # 具体Agent
    "ManagerAgent",
    "ProfessorAgent",
    "ArchitectAgent",
    "ExaminerAgent",
    "DirectorAgent",
    "HackerAgent",
    "ReviewerAgent",

    # 工具集
    "MarkdownGeneratorTool",  # 实际使用中
    # "AcademicSearchTool",       # [已注释] 预留 Phase 1
    # "AcademicSearchResult",     # [已注释] 预留 Phase 1
    # "ToolRegistry",             # [已注释] 预留 Phase 1

    # 类型定义
    "AgentConfig",
    "AgentContext",
    "AgentResult",
    "AgentExecutionResult",
    "AgentStatusInfo",
    "AgentStatus",
    "AgentType",
]
