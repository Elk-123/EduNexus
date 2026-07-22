"""
Fallback 降级 Hook — 统一处理 LLM 调用失败时的降级策略

当前 v2.0 的降级逻辑分散在每个 Agent 的 execute() 中 (try/except → get_fallback_content)。
此 Hook 提供集中的降级策略配置，支持:
  - LLM 调用失败 → 自动返回 fallback_data
  - 输出校验失败 → 自动重试 (最多 N 次)
  - 重试耗尽 → 返回 fallback_data

使用方式:
    from .hooks.fallback_hook import FallbackCallback
    result = pipeline.invoke(
        state,
        config={"callbacks": [FallbackCallback(max_retries=2)]}
    )

[建议] Phase 5 (反思与自愈) 时扩展:
  - 添加 Reflection 机制：将 Reviewer 的 feedback 注入上游 Agent 重新生成
  - 添加 escalation 策略：3次重试后切换模型 (如 deepseek-chat → deepseek-reasoner)
"""
import logging
from typing import Any, Dict, Optional

from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger("edunexus.agents")


class FallbackCallback(BaseCallbackHandler):
    """
    Fallback 降级回调 — 监控 LLM 错误并执行降级策略。

    [建议] 当前版本仅记录错误，实际的 fallback 逻辑仍在 graph/nodes.py 中处理。
           Phase 5 时可将 fallback 逻辑完全迁移到此处。
    """

    def __init__(self, max_retries: int = 0):
        """
        Args:
            max_retries: LLM 调用失败后的最大重试次数 (0=不重试)
        """
        super().__init__()
        self.max_retries = max_retries
        self._error_counts: Dict[str, int] = {}
        self._fallback_used: Dict[str, bool] = {}

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """LLM 调用失败时记录"""
        # 按 parent_run_id (Agent Node) 分组计数
        key = parent_run_id or run_id
        self._error_counts[key] = self._error_counts.get(key, 0) + 1
        count = self._error_counts[key]

        logger.warning(
            "[Fallback Hook] LLM error (attempt %d/%d): %s",
            count, self.max_retries + 1, error,
        )

        # [建议] Phase 5: 根据 error 类型决策
        # if isinstance(error, RateLimitError):
        #     等待后重试
        # elif isinstance(error, AuthenticationError):
        #     切换备用 API key
        # else:
        #     返回 fallback_data

    def mark_fallback_used(self, agent_id: str) -> None:
        """标记某个 Agent 已使用 fallback 数据"""
        self._fallback_used[agent_id] = True
        logger.info("[Fallback Hook] %s: fallback data used", agent_id)

    def was_fallback_used(self, agent_id: str) -> bool:
        """检查某个 Agent 是否使用了 fallback 数据"""
        return self._fallback_used.get(agent_id, False)

    def get_error_summary(self) -> dict:
        """获取错误摘要 (用于管道结束后的诊断报告)"""
        return {
            "total_llm_errors": sum(self._error_counts.values()),
            "fallback_agents": [k for k, v in self._fallback_used.items() if v],
        }
