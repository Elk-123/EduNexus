"""
Agent协调器 - 负责管理所有Agent的执行流程，支持上下文累积传递
"""
import uuid
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..types import (
    AgentConfig, AgentContext, AgentExecutionResult, AgentStatusInfo,
    AgentStatus, AgentType
)
from ..base.BaseAgent import BaseAgent

logger = logging.getLogger("edunexus.agents")


class AgentCoordinator:
    """Agent协调器 — 顺序执行Agent并累积传递上下文"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_states: Dict[str, AgentStatusInfo] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """注册Agent"""
        config = agent.get_config()
        self.agents[config.id] = agent
        self.agent_states[config.id] = AgentStatusInfo(
            agent_id=config.id,
            status=AgentStatus.IDLE,
            last_updated=datetime.now(),
            success_count=0,
            failure_count=0
        )
        logger.info("Registered agent: %s (%s)", config.id, config.name)

    def execute_pipeline(
        self, topic: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行Agent流水线（同步），支持上下文累积

        Args:
            topic: 生成主题
            context: 初始上下文（可选，如用户偏好）

        Returns:
            {
                "results": List[AgentExecutionResult],
                "accumulated_context": Dict[str, Any],  # 所有Agent输出的累积
                "task_id": str,
            }
        """
        results: List[AgentExecutionResult] = []

        # 累积上下文：key=agent_id, value=该Agent产出的content
        accumulated: Dict[str, Any] = context.copy() if context else {}
        task_id = self._generate_task_id()

        execution_context = AgentContext(
            task_id=task_id,
            topic=topic,
            context=accumulated
        )

        # Agent执行顺序
        agent_order = [
            AgentType.MANAGER,
            AgentType.PROFESSOR,
            AgentType.ARCHITECT,
            AgentType.EXAMINER,
            AgentType.DIRECTOR,
            AgentType.HACKER,
            AgentType.REVIEWER
        ]

        for agent_type in agent_order:
            agent = self.agents.get(agent_type.value)
            if not agent:
                logger.warning("Agent %s not registered, skipping", agent_type.value)
                continue

            try:
                self._update_agent_status(agent_type.value, AgentStatus.RUNNING)

                start_time = datetime.now()
                result = agent.execute(execution_context)
                end_time = datetime.now()

                # 使用协调器测量的墙钟时间（毫秒）
                result.duration = int((end_time - start_time).total_seconds() * 1000)
                results.append(result)

                # 更新状态
                if result.status == AgentStatus.SUCCESS:
                    self._increment_success_count(agent_type.value)
                    # ★ 核心：将成功Agent的输出累积到上下文
                    if result.result and result.result.content:
                        accumulated[agent_type.value] = result.result.content
                        execution_context.context = accumulated
                else:
                    self._increment_failure_count(agent_type.value)

                self._update_agent_status(agent_type.value, result.status)
                logger.debug(
                    "Agent %s completed: status=%s duration=%dms",
                    agent_type.value, result.status, result.duration
                )

            except Exception as error:
                logger.error("Error executing agent %s: %s", agent_type.value, error)
                self._update_agent_status(agent_type.value, AgentStatus.ERROR)
                results.append(AgentExecutionResult(
                    agent_id=agent_type.value,
                    status=AgentStatus.ERROR,
                    error=str(error),
                    duration=0
                ))

        return {
            "results": results,
            "accumulated_context": accumulated,
            "task_id": task_id,
        }

    # ═══════════════════════════════════════════════════════════
    #  ★ v2.1 NEW: LangGraph 执行方法
    #    使用 graph/ 模块中的 StateGraph 替代手动顺序遍历
    #    旧 execute_pipeline() 保持不变，保证向后兼容
    # ═══════════════════════════════════════════════════════════

    def execute_pipeline_graph(
        self, topic: str, context: Optional[Dict[str, Any]] = None,
        callbacks: Optional[list] = None,
        agent_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """[v2.1] 通过 LangGraph StateGraph 执行管道。

        与 execute_pipeline() 的返回格式完全一致，可作为 drop-in 替换。

        Args:
            topic: 生成主题
            context: 初始上下文（可选）
            callbacks: LangChain 回调列表（用于 LLM/Tool 级回调）
            agent_callback: Agent 级回调 (agent_id, event_type, data) -> None
                           由 WSBroadcastCallback.create_agent_callback() 创建

        Returns:
            {"results", "accumulated_context", "task_id"}
        """
        from ..graph.pipeline import get_pipeline, create_initial_state

        # 创建初始状态
        initial_state = create_initial_state(topic, context)

        # 注入 Agent 事件回调（供 graph nodes 在执行前后调用）
        if agent_callback:
            initial_state["_agent_event"] = agent_callback

        # 执行管道
        pipeline = get_pipeline()
        config = {"callbacks": callbacks} if callbacks else {}
        final_state = pipeline.invoke(initial_state, config=config)

        # 转换为 v2.0 兼容的返回格式
        from ..types import AgentExecutionResult, AgentResult, AgentStatus

        results = []
        for r in final_state.get("results", []):
            results.append(AgentExecutionResult(
                agent_id=r["agent_id"],
                status=AgentStatus(r["status"]),
                result=AgentResult(
                    content=r["result"]["content"],
                    type=r["result"]["type"],
                    timestamp=datetime.now(),
                    log=r["result"].get("log", []),
                ) if r.get("result") else None,
                duration=r.get("duration", 0),
            ))

        logger.info(
            "[Graph] Pipeline completed: %s, %d agents, %d errors",
            final_state["task_id"],
            len(results),
            final_state.get("error_count", 0),
        )

        return {
            "results": results,
            "accumulated_context": final_state.get("agent_outputs", {}),
            "task_id": final_state["task_id"],
        }

    async def execute_pipeline_graph_async(
        self, topic: str, context: Optional[Dict[str, Any]] = None,
        callbacks: Optional[list] = None,
    ):
        """[v2.1] 异步流式执行管道 — 返回事件流（用于 WebSocket 实时推送）。

        与 execute_pipeline_graph() 不同的是，此方法通过 astream_events()
        产出细粒度事件，前端可以实时看到每个 Agent 的执行进度。

        Yields:
            dict: LangChain 事件对象

        Usage:
            async for event in coordinator.execute_pipeline_graph_async(
                topic, callbacks=[WSBroadcastCallback(...)]
            ):
                # event 是 LangChain astream_events v2 格式
                print(event["event"], event["name"])
        """
        from ..graph.pipeline import get_pipeline, create_initial_state

        initial_state = create_initial_state(topic, context)
        pipeline = get_pipeline()
        config = {"callbacks": callbacks} if callbacks else {}

        async for event in pipeline.astream_events(initial_state, config=config, version="v2"):
            yield event

    # ── 私有方法 ─────────────────────────────────────────────
    # def get_agent_status(self, agent_id: str) -> Optional[AgentStatusInfo]:
    #     """获取Agent状态"""
    #     return self.agent_states.get(agent_id)

    # def get_all_agent_statuses(self) -> List[AgentStatusInfo]:
    #     """获取所有Agent状态"""
    #     return list(self.agent_states.values())

    def _update_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """更新Agent状态"""
        agent_status = self.agent_states.get(agent_id)
        if agent_status:
            agent_status.status = status
            agent_status.last_updated = datetime.now()

    def _increment_success_count(self, agent_id: str) -> None:
        """增加成功计数"""
        agent_status = self.agent_states.get(agent_id)
        if agent_status:
            agent_status.success_count += 1

    def _increment_failure_count(self, agent_id: str) -> None:
        """增加失败计数"""
        agent_status = self.agent_states.get(agent_id)
        if agent_status:
            agent_status.failure_count += 1

    def _generate_task_id(self) -> str:
        """生成任务ID"""
        return f"task_{uuid.uuid4().hex[:12]}"
