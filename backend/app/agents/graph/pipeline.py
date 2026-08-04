"""
LangGraph 管道编译 — 构建 Agent 执行 StateGraph

使用方式:
    pipeline = build_pipeline()
    final_state = pipeline.invoke(initial_state)
    # 或流式:
    async for event in pipeline.astream_events(initial_state, version="v2"):
        ...

Phase 升级路径:
  - Phase 1 (当前): 顺序执行，保持 v2.0 兼容
  - Phase 2: 改为并行边 (professor/architect/examiner/director/hacker 从 manager 后并行)
  - Phase 3: 添加 conditional_edges (Manager 动态决策执行哪些 Agent)
  - Phase 4: 添加 checkpoint 持久化 (SqliteSaver/RedisSaver)
  - Phase 5: Reviewer 反馈 → 上游 Agent 重试 (Reflection loop)
"""
import uuid
import logging
from typing import Optional

from langgraph.graph import StateGraph, END

from .state import PipelineState
from .nodes import NODES
from ..types import AgentType

logger = logging.getLogger("edunexus.agents")

# Agent 执行顺序 (Phase 1: 顺序执行)
AGENT_ORDER = [
    AgentType.MANAGER.value,
    AgentType.PROFESSOR.value,
    AgentType.ARCHITECT.value,
    AgentType.EXAMINER.value,
    AgentType.DIRECTOR.value,
    AgentType.HACKER.value,
    AgentType.REVIEWER.value,
]


def build_pipeline() -> StateGraph:
    """
    构建 LangGraph StateGraph 管道。

    Phase 1: 顺序执行 (manager → professor → ... → reviewer → END)
    Phase 2: 并行分支 (manager → [professor, architect, examiner, director, hacker] → reviewer)

    Returns:
        CompiledStateGraph: 编译后的可执行图
    """
    builder = StateGraph(PipelineState)

    # ── 添加节点 ──
    for agent_id in AGENT_ORDER:
        node_fn = NODES.get(agent_id)
        if node_fn is None:
            logger.warning("No node function for agent '%s', skipping", agent_id)
            continue
        builder.add_node(agent_id, node_fn)

    # ── v2.4: 并行 + 反思闭环 ──
    builder.set_entry_point("manager")
    for agent_id in AGENT_ORDER[1:-1]:  # professor ~ hacker
        builder.add_edge("manager", agent_id)
        builder.add_edge(agent_id, "reviewer")

    # 反思闭环: Reviewer 评分 < 70 → Professor 重写 → Reviewer 再评
    def _should_retry(state: PipelineState) -> str:
        feedback = state.get("reviewer_feedback")
        retries = state.get("retry_count", 0)
        if feedback and retries < 2:
            logger.info("[Reflect] 触发重试 #%d → Professor", retries)
            return "professor"
        logger.info("[Reflect] 审查通过 (retries=%d) → END", retries)
        return END

    builder.add_conditional_edges("reviewer", _should_retry, {
        "professor": "professor",
        END: END,
    })

    # [v2.2 legacy] 顺序边 — 保留注释备查
    # builder.set_entry_point(AGENT_ORDER[0])
    # for i in range(len(AGENT_ORDER) - 1):
    #     builder.add_edge(AGENT_ORDER[i], AGENT_ORDER[i + 1])
    # builder.add_edge(AGENT_ORDER[-1], END)

    # ── [Phase 4 预留] Checkpoint ──
    # from langgraph.checkpoint.memory import MemorySaver
    # memory = MemorySaver()
    # return builder.compile(checkpointer=memory)

    return builder.compile()


def create_initial_state(topic: str, context: Optional[dict] = None) -> PipelineState:
    """
    创建管道初始状态。

    Args:
        topic: 生成主题
        context: 可选初始上下文 (如用户偏好)
    """
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    return PipelineState(
        topic=topic,
        task_id=task_id,
        agent_outputs=context or {},
        messages=[],
        current_agent="",
        agent_order=AGENT_ORDER,
        agent_index=0,
        results=[],
        final_report=None,
        error_count=0,
        retry_count=0,
        reviewer_feedback=None,
    )


# ── 全局管道实例 ──
# [建议] 生产环境中，如果使用 MemorySaver checkpoint，
#        每个请求应创建新的 pipeline 实例以避免状态交叉污染。
#        当前无 checkpoint，单例安全。
_pipeline = None


def get_pipeline() -> StateGraph:
    """获取全局管道单例（懒加载）"""
    global _pipeline
    if _pipeline is None:
        _pipeline = build_pipeline()
        logger.info("[Graph] Pipeline compiled with %d agents", len(AGENT_ORDER))
    return _pipeline
