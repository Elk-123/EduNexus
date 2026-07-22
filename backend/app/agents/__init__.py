"""
Agent模块主入口 — 导出所有Agent相关功能

v2.1 新增模块 (LangGraph 架构):
  - schemas/     : 结构化输出 Pydantic 模型
  - prompts/     : 集中 Prompt 模板管理
  - graph/       : LangGraph StateGraph 管道
  - hooks/       : 生命周期回调 (日志/WS广播/降级)
  - tools/       : @tool 装饰器工具 (学术搜索/Web搜索/代码执行)

注意: LangChainUtils 依赖 langchain_openai 包，仅在调用 initialize_model() 时才需要。
      graph/ 模块依赖 langgraph 包，如果未安装则 graph 相关功能不可用。
"""

# ── 基础类 ──
from .base.BaseAgent import BaseAgent

# ── 协调器 ──
from .coordinator.AgentCoordinator import AgentCoordinator

# ── 具体Agent实现 ──
from .implementations.ManagerAgent import ManagerAgent
from .implementations.ProfessorAgent import ProfessorAgent
from .implementations.ArchitectAgent import ArchitectAgent
from .implementations.ExaminerAgent import ExaminerAgent
from .implementations.DirectorAgent import DirectorAgent
from .implementations.HackerAgent import HackerAgent
from .implementations.ReviewerAgent import ReviewerAgent

# ── 工具集 ──
from .tools.markdown_generator import MarkdownGeneratorTool  # 被 agent_orchestrator.py / factory.py 实际使用

# [v2.1] @tool 工具（如果 langchain_core 可用）
try:
    from .tools.academic_search import academic_search_tool
    from .tools.web_search import web_search_tool
    from .tools.code_executor import code_executor_tool
    _TOOLS_AVAILABLE = True
except ImportError:
    academic_search_tool = None  # type: ignore
    web_search_tool = None  # type: ignore
    code_executor_tool = None  # type: ignore
    _TOOLS_AVAILABLE = False

# ── 类型定义 ──
from .types import (
    AgentConfig, AgentContext, AgentResult, AgentExecutionResult, AgentStatusInfo,
    AgentStatus, AgentType
)

# ── LangChainUtils 延迟导入（需要 langchain_openai 包）──
try:
    from .utils.LangChainUtils import LangChainUtils
except ImportError:
    LangChainUtils = None  # type: ignore

# ── [v2.1] LangGraph 模块（需要 langgraph 包）──
try:
    from .graph import (
        PipelineState, NODES,
        build_pipeline, create_initial_state, get_pipeline, AGENT_ORDER,
    )
    _GRAPH_AVAILABLE = True
except ImportError:
    PipelineState = None  # type: ignore
    NODES = None  # type: ignore
    build_pipeline = None  # type: ignore
    create_initial_state = None  # type: ignore
    get_pipeline = None  # type: ignore
    AGENT_ORDER = None  # type: ignore
    _GRAPH_AVAILABLE = False

# ── [v2.1] Hooks 模块（需要 langchain_core 包）──
try:
    from .hooks import LoggingCallback, WSBroadcastCallback, FallbackCallback
    _HOOKS_AVAILABLE = True
except ImportError:
    LoggingCallback = None  # type: ignore
    WSBroadcastCallback = None  # type: ignore
    FallbackCallback = None  # type: ignore
    _HOOKS_AVAILABLE = False

# ── [v2.1] Schemas + Prompts (纯 Python，无额外依赖) ──
from .schemas import (
    ManagerOutput, ProfessorOutput, ArchitectOutput,
    ExaminerOutput, DirectorOutput, HackerOutput, ReviewerOutput,
)
from .prompts import PROMPTS


__all__ = [
    # ── 基础类 ──
    "BaseAgent",

    # ── 协调器 ──
    "AgentCoordinator",

    # ── 工具类 ──
    "LangChainUtils",

    # ── 具体Agent ──
    "ManagerAgent",
    "ProfessorAgent",
    "ArchitectAgent",
    "ExaminerAgent",
    "DirectorAgent",
    "HackerAgent",
    "ReviewerAgent",

    # ── 工具集 ──
    "MarkdownGeneratorTool",
    "academic_search_tool",
    "web_search_tool",
    "code_executor_tool",

    # ── 类型定义 ──
    "AgentConfig",
    "AgentContext",
    "AgentResult",
    "AgentExecutionResult",
    "AgentStatusInfo",
    "AgentStatus",
    "AgentType",

    # ── [v2.1] LangGraph ──
    "PipelineState",
    "NODES",
    "build_pipeline",
    "create_initial_state",
    "get_pipeline",
    "AGENT_ORDER",

    # ── [v2.1] Hooks ──
    "LoggingCallback",
    "WSBroadcastCallback",
    "FallbackCallback",

    # ── [v2.1] Schemas + Prompts ──
    "ManagerOutput",
    "ProfessorOutput",
    "ArchitectOutput",
    "ExaminerOutput",
    "DirectorOutput",
    "HackerOutput",
    "ReviewerOutput",
    "PROMPTS",
]
