"""
Agent基类抽象定义
"""
# [已注释] import threading — 未使用（interrupt/is_stopped 机制预留 Phase 2）
from datetime import datetime
from abc import ABC, abstractmethod
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentStatusInfo, AgentStatus


class BaseAgent(ABC):
    """Agent基类 — 所有具体Agent必须继承此类"""

    def __init__(self, config: AgentConfig):
        self.config = config
        # [已注释] self.system_prompt = self._build_system_prompt()
        #   system_prompt 从未被读取（各 Agent 通过 LangChainUtils.create_prompt_template 设置自己的 prompt）

        # 内部状态追踪
        self._state = {
            "status": AgentStatus.IDLE,
            "success_count": 0,
            "failure_count": 0,
            "last_updated": datetime.now(),
            "current_task": None,
        }
        # [已注释] self._should_stop = threading.Event()
        #   interrupt/is_stopped 机制预留 Phase 2 并行执行

    # ── 公共接口 ─────────────────────────────────────────────

    def get_config(self) -> AgentConfig:
        """获取Agent配置"""
        return self.config

    # [已注释] get_system_prompt — 从未被调用（各 Agent 通过 LangChainUtils 设置 prompt）
    # def get_system_prompt(self) -> str:
    #     """获取系统提示词（供子类注入LLM调用）"""
    #     return self.system_prompt

    @abstractmethod
    def execute(self, context: AgentContext) -> AgentExecutionResult:
        """执行Agent任务（同步）— 子类必须实现"""
        pass

    def get_status(self) -> AgentStatusInfo:
        """获取Agent运行时状态（读取内部_state）"""
        return AgentStatusInfo(
            agent_id=self.config.id,
            status=self._state["status"],
            last_updated=self._state["last_updated"],
            current_task=self._state["current_task"],
            success_count=self._state["success_count"],
            failure_count=self._state["failure_count"],
        )

    # [已注释] interrupt/is_stopped — 预留 Phase 2 并行执行中断机制
    # def interrupt(self) -> None:
    #     """中断执行 — 设置停止标志"""
    #     self._should_stop.set()

    # def is_stopped(self) -> bool:
    #     """检查是否已被中断"""
    #     return self._should_stop.is_set()

    # ── 内部方法 ─────────────────────────────────────────────

    # [已注释] _update_state — 从未被调用（_record_success/failure 直接操作 _state）
    # def _update_state(self, **kwargs) -> None:
    #     """更新内部状态"""
    #     self._state.update(kwargs)
    #     self._state["last_updated"] = datetime.now()

    def _record_success(self, task: str = None) -> None:
        """记录一次成功执行"""
        self._state["success_count"] += 1
        self._state["status"] = AgentStatus.IDLE
        self._state["last_updated"] = datetime.now()
        if task:
            self._state["current_task"] = task

    def _record_failure(self, task: str = None) -> None:
        """记录一次失败执行"""
        self._state["failure_count"] += 1
        self._state["status"] = AgentStatus.ERROR
        self._state["last_updated"] = datetime.now()
        if task:
            self._state["current_task"] = task

    # [已注释] _build_system_prompt — 从未被使用（各 Agent 的 system prompt 由 LangChainUtils.create_prompt_template 提供）
    # def _build_system_prompt(self) -> str:
    #     return (
    #         f"You are a {self.config.role} agent. "
    #         "ALWAYS output thought process in <thought> tags BEFORE any tool call or final answer.\n"
    #         "Example: <thought>Need to search for academic papers on {topic}</thought>"
    #     )
