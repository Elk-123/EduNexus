"""
日志回调 Hook — 基于 LangChain BaseCallbackHandler

用框架的标准回调机制替代各 Agent 中散布的 logger.info/warning 调用。
所有 LLM 调用 / Chain 执行 / Tool 调用的日志集中在此处理。

使用方式:
    from .hooks.logging_hook import LoggingCallback
    result = pipeline.invoke(state, config={"callbacks": [LoggingCallback()]})
"""
import logging
import time
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

logger = logging.getLogger("edunexus.agents")


class LoggingCallback(BaseCallbackHandler):
    """
    统一日志回调 — 记录 LLM 调用 / Chain 执行 / Tool 调用。

    [建议] 可以扩展为:
      - 记录每次 LLM 调用的 token 消耗
      - 记录每次 Tool 调用的参数和返回值
      - 将日志写入数据库 / 发送到监控系统
    """

    def __init__(self, task_id: str = ""):
        super().__init__()
        self.task_id = task_id
        self._start_times: Dict[str, float] = {}
        # [建议] 添加 token 计数器
        # self._total_tokens = 0

    def _prefix(self) -> str:
        if self.task_id:
            return f"[{self.task_id}]"
        return ""

    # ── LLM 回调 ──

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._start_times[run_id] = time.time()
        prompt_preview = str(prompts[0])[:200] if prompts else "(no prompt)"
        logger.info("%s [LLM Start] prompt preview: %s...", self._prefix(), prompt_preview)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        elapsed = time.time() - self._start_times.pop(run_id, 0)
        content_preview = ""
        if response.generations and response.generations[0]:
            text = getattr(response.generations[0][0], "text", "")
            if hasattr(response.generations[0][0], "message"):
                text = str(response.generations[0][0].message.content)
            content_preview = text[:300]
        logger.info(
            "%s [LLM End] duration=%.1fs, response preview: %s",
            self._prefix(), elapsed, content_preview,
        )

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._start_times.pop(run_id, None)
        logger.error("%s [LLM Error] %s", self._prefix(), error)

    # ── Chain 回调 ──

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        chain_name = serialized.get("name", serialized.get("id", "unknown"))
        logger.debug("%s [Chain Start] %s", self._prefix(), chain_name)

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug("%s [Chain End]", self._prefix())

    # ── Tool 回调 ──

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        tool_name = serialized.get("name", "unknown")
        self._start_times[run_id] = time.time()
        logger.info("%s [Tool Start] %s(%s)", self._prefix(), tool_name, input_str[:100])

    def on_tool_end(
        self,
        output: str,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        elapsed = time.time() - self._start_times.pop(run_id, 0)
        logger.info("%s [Tool End] duration=%.1fs, output: %s...", self._prefix(), elapsed, output[:200])

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._start_times.pop(run_id, None)
        logger.error("%s [Tool Error] %s", self._prefix(), error)
