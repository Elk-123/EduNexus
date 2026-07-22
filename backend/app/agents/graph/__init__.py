"""
LangGraph Agent 管道模块

提供:
  - PipelineState: 管道共享状态 TypedDict
  - NODES: 7 个 Agent 节点函数
  - build_pipeline(): 构建编译后的 StateGraph
  - create_initial_state(): 创建初始状态
  - get_pipeline(): 获取全局管道单例
"""
from .state import PipelineState
from .nodes import NODES, manager_node, professor_node, architect_node, examiner_node, director_node, hacker_node, reviewer_node
from .pipeline import build_pipeline, create_initial_state, get_pipeline, AGENT_ORDER

__all__ = [
    "PipelineState",
    "NODES",
    "manager_node",
    "professor_node",
    "architect_node",
    "examiner_node",
    "director_node",
    "hacker_node",
    "reviewer_node",
    "build_pipeline",
    "create_initial_state",
    "get_pipeline",
    "AGENT_ORDER",
]
