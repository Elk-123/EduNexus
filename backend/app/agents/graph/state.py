"""
LangGraph 管道共享状态 — PipelineState TypedDict

并行模式 (v2.4): agent_outputs / results / error_count 使用 reducer 自动合并，
                支持 5 个专家 Agent 并行执行。
"""
from typing import TypedDict, Annotated, Optional, Any, Callable
from operator import add
from langgraph.graph.message import add_messages


def _merge_dicts(left: dict, right: dict) -> dict:
    """Reducer: 合并两个 dict（并行 node 各自返回部分 agent_outputs）"""
    return {**left, **right}


def _merge_lists(left: list, right: list) -> list:
    """Reducer: 合并两个 list（用于 results 追加）"""
    if left is None:
        return right or []
    if right is None:
        return left or []
    return left + right


def _add_ints(left: int | None, right: int | None) -> int:
    """Reducer: 累加 int（用于 error_count）"""
    return (left or 0) + (right or 0)


def _last_value(left, right):
    """Reducer: 取最后一次写入的值（用于 current_agent 等）"""
    return right


class PipelineState(TypedDict):
    """Agent 管道全局状态"""

    # ── 输入 ──
    topic: str
    task_id: str

    # ── 上下文累积 (reducer: 并行安全合并) ──
    agent_outputs: Annotated[dict, _merge_dicts]

    # ── 消息历史 ──
    messages: Annotated[list, add_messages]

    # ── 执行追踪 ──
    current_agent: Annotated[str, _last_value]  # 并行模式: 取最后更新的值
    agent_order: list[str]
    agent_index: int

    # ── 输出 (reducer) ──
    results: Annotated[list, _merge_lists]
    final_report: Optional[str]
    error_count: Annotated[int, _add_ints]

    # ── 反思闭环 (v2.4) ──
    retry_count: Annotated[int, _add_ints]       # 重试次数 (0 → 1 → 2 max)
    reviewer_feedback: Optional[dict]             # Reviewer 低分时的改进建议

    # ── 内部回调 ──
    _agent_event: Optional[Callable[[str, str, Optional[dict]], None]]
