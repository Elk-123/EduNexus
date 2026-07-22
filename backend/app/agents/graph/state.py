"""
LangGraph 管道共享状态 — PipelineState TypedDict

LangGraph 的状态管理机制:
  - 每个 Node 函数接收 state，返回部分更新的 dict
  - LangGraph 自动将返回的 dict 合并到全局 state（reducer 机制）
  - Annotated[list, add_messages] 自动追加消息而非覆盖
  - 不需要像 v2.0 那样手动传递 accumulated_context dict
"""
from typing import TypedDict, Annotated, Optional, Any, Callable
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class PipelineState(TypedDict):
    """Agent 管道全局状态 — 在 7 个 Node 之间共享"""

    # ── 输入字段 ──
    topic: str                         # 用户输入主题
    task_id: str                       # 任务 ID

    # ── 上下文累积 ──
    agent_outputs: dict                # agent_id → content，累积所有 Agent 输出
    # [建议] 改用 Annotated[dict, merge_dict] reducer 自动合并
    #        当前保留手动合并方式以保证向后兼容

    # ── 消息历史 ──
    messages: Annotated[list, add_messages]  # 对话历史（LangGraph 自动追加）

    # ── 执行追踪 ──
    current_agent: str                 # 当前正在执行的 agent_id
    agent_order: list[str]             # Agent 执行顺序列表
    agent_index: int                   # 当前执行到的索引位置

    # ── 输出字段 ──
    results: list[dict]                # AgentExecutionResult 的 dict 列表
    final_report: Optional[str]        # Markdown 最终报告（Reviewer 完成后生成）
    error_count: int                   # 累计错误次数

    # ── 元数据 ──
    # [建议] 添加 started_at, completed_at 时间戳用于性能监控

    # ── 内部回调（由 execute_pipeline_graph 注入）──
    # Agent node 在执行前后调用: callback(agent_id, event_type, data)
    _agent_event: Optional[Callable[[str, str, Optional[dict]], None]]
