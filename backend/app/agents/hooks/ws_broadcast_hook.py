"""
WebSocket 广播 Hook — 将 Agent 执行状态通过 WebSocket 实时推送给前端

解耦 Agent 逻辑和传输层:
  - Agent 代码中不再需要手动调用 ws_manager.broadcast()
  - 广播逻辑集中在 Hook 中，通过 LangChain 回调机制触发
  - 未来切换推送方式（SSE / MQTT / gRPC stream）只需改 Hook

使用方式:
    from .hooks.ws_broadcast_hook import WSBroadcastCallback
    result = pipeline.invoke(
        state,
        config={"callbacks": [WSBroadcastCallback(task_id, main_loop, agent_names)]}
    )

对应 v2.0 中 agent_orchestrator.py 和 factory.py 内的 make_wrapper() 广播逻辑。
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger("edunexus.agents")

# 延迟导入以避免循环依赖
_ws_manager = None


def _get_ws_manager():
    """延迟获取 WebSocket 管理器实例"""
    global _ws_manager
    if _ws_manager is None:
        try:
            from app.core.websocket import ws_manager as wsm

            _ws_manager = wsm
        except ImportError:
            logger.warning("WebSocket manager not available — WS broadcast disabled")
            _ws_manager = False  # sentinel
    return _ws_manager if _ws_manager is not False else None


class WSBroadcastCallback(BaseCallbackHandler):
    """
    WebSocket 广播回调 — 自动将 Agent 状态变更推送到前端。

    每个 LangGraph Node 开始/结束时触发广播，与 v2.0 中 agent_orchestrator 的
    make_wrapper() 行为一致。

    [建议] 扩展方向:
      - 区分 on_chain_start 的 chain 类型，只对 Agent Node 广播
      - 添加进度百分比 (当前第几个 Agent / 总共几个)
      - 添加 estimated_time_remaining 字段
    """

    def __init__(
        self,
        task_id: str,
        loop: asyncio.AbstractEventLoop,
        agent_names: Optional[Dict[str, str]] = None,
    ):
        super().__init__()
        self.task_id = task_id
        self.loop = loop
        self.agent_names = agent_names or {
            "manager": "Manager",
            "professor": "Professor",
            "architect": "Architect",
            "examiner": "Examiner",
            "director": "Director",
            "hacker": "Hacker",
            "reviewer": "Reviewer",
        }
        # 用 run_id 追踪当前正在执行的 Agent（线程安全）
        # key = run_id, value = agent_display_name
        self._run_agent_map: Dict[str, str] = {}

    def _broadcast(self, data: dict) -> None:
        """线程安全地广播消息到 WebSocket"""
        wsm = _get_ws_manager()
        if wsm is None:
            return
        try:
            asyncio.run_coroutine_threadsafe(
                wsm.broadcast(self.task_id, data), self.loop
            )
        except Exception as e:
            logger.warning("WS broadcast failed: %s", e)

    def _broadcast_agent_status(self, agent_name: str, status: str) -> None:
        """广播 Agent 状态变更"""
        self._broadcast({
            "type": "agent_status",
            "agent": agent_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def _broadcast_agent_log(self, agent_name: str, message: str, msg_type: str = "info") -> None:
        """广播 Agent 日志"""
        self._broadcast({
            "type": "agent_log",
            "agent": agent_name,
            "message": message,
            "type": msg_type,
            "timestamp": datetime.utcnow().isoformat(),
        })

    # ── Chain 回调 (每个 Agent Node 是一个 Chain) ──

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Agent Node 开始执行"""
        if serialized is None:
            return  # LangGraph 内部 chain，无序列化信息，跳过
        chain_name = serialized.get("name", serialized.get("id", ""))
        # 只处理 Agent Node（过滤掉内部的 LLM chain）
        agent_display = self.agent_names.get(chain_name, "")
        if agent_display:
            self._run_agent_map[run_id] = agent_display  # 记录映射
            self._broadcast_agent_status(agent_display, "running")
            self._broadcast_agent_log(agent_display, f"开始执行 {agent_display}...", "info")

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Agent Node 执行完成 — 通过 run_id 找回 Agent 名称"""
        agent_display = self._run_agent_map.pop(run_id, "")
        if agent_display:
            self._broadcast_agent_status(agent_display, "success")
            self._broadcast_agent_log(agent_display, "完成 ✓", "success")

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Agent Node 执行失败"""
        logger.error("[WS Hook] Chain error: %s", error)

    # ── LLM 回调 ──

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id=None, **kwargs):
        """LLM 调用开始（可选：广播"正在生成..."）"""
        pass  # 当前 v2.0 不在 LLM 级别广播，保留扩展点

    def on_llm_end(self, response, *, run_id, parent_run_id=None, **kwargs):
        """LLM 调用完成"""
        pass

    # ── Tool 回调 ──

    def on_tool_start(self, serialized, input_str, *, run_id, parent_run_id=None, **kwargs):
        """Tool 开始执行"""
        tool_name = serialized.get("name", "tool")
        self._broadcast_agent_log("System", f"🔧 调用工具: {tool_name}", "info")

    def on_tool_end(self, output, *, run_id, parent_run_id=None, **kwargs):
        """Tool 执行完成"""
        pass

    # ═══════════════════════════════════════════════════════════
    #  工厂方法: 创建 state-based Agent 事件回调
    #  用于 graph/nodes.py 的 _agent_event 机制
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def create_agent_callback(task_id: str, loop, agent_names: Optional[Dict[str, str]] = None):
        """
        创建适配 graph/nodes.py 的 Agent 事件回调函数。

        签名: callback(agent_id, event_type, data) -> None

        用于 graph pipeline 的 _agent_event 字段。
        不需要依赖 LangChain 的 on_chain_start/on_chain_end 回调机制。

        Args:
            task_id: WebSocket 任务 ID
            loop: 主线程 event loop（用于 run_coroutine_threadsafe）
            agent_names: agent_id → 显示名称映射

        Returns:
            callable: (agent_id, event_type, data) -> None
        """
        hook = WSBroadcastCallback(task_id, loop, agent_names)

        def agent_callback(agent_id: str, event_type: str, data: dict = None):
            display_name = hook.agent_names.get(agent_id, agent_id)
            if event_type == "start":
                hook._broadcast_agent_status(display_name, "running")
                hook._broadcast_agent_log(display_name, f"开始执行 {display_name}...", "info")
            elif event_type == "done":
                if data and data.get("status") == "fallback":
                    hook._broadcast_agent_status(display_name, "success")
                    hook._broadcast_agent_log(
                        display_name,
                        f"完成 (降级): {data.get('error', 'unknown')}",
                        "warn",
                    )
                else:
                    hook._broadcast_agent_status(display_name, "success")
                    hook._broadcast_agent_log(display_name, "完成 ✓", "success")

        return agent_callback
