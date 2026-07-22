"""
LangChain集成工具类 - Open AI版本

需要安装 langchain-openai 和 langchain-core:
    pip install langchain-openai langchain-core
"""

import json
import re
# [已注释] import threading — 当前为同步顺序执行，线程锁不需要（预留 Phase 2 并行）
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()  # 读取 .env 文件内容并写入系统环境变量

logger = logging.getLogger("edunexus.agents")

_model = None
# [已注释] _model_lock = threading.Lock() — 顺序执行无需锁（预留 Phase 2 并行）

# 延迟导入
ChatOpenAI = None
ChatPromptTemplate = None


def _ensure_langchain():
    """延迟加载 LangChain 依赖"""
    global ChatOpenAI, ChatPromptTemplate
    if ChatOpenAI is not None:
        return
    try:
        from langchain_openai import ChatOpenAI as _ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate as _ChatPromptTemplate

        ChatOpenAI = _ChatOpenAI
        ChatPromptTemplate = _ChatPromptTemplate
    except ImportError as e:
        raise ImportError(
            "langchain-openai and langchain-core are required. "
            "Install with: pip install langchain-openai langchain-core"
        ) from e


class LangChainUtils:
    """LangChain工具类 (Open API)"""

    @classmethod
    def initialize_model(cls, api_key: str, model_name: str = "deepseek-chat", base_url: str = "https://api.deepseek.com") -> None:
        """初始化open ai LangChain模型（线程安全）

        Args:
            api_key: DeepSeek API Key/openai API Key
            model_name: 模型名称，默认 deepseek-chat
                        可选: deepseek-chat, deepseek-reasoner
        """
        global _model
        _ensure_langchain()
        # [已注释] with _model_lock: — 顺序执行无需锁
        _model = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
        )
        logger.info("LangChain model initialized: %s via %s", model_name, base_url)

    @classmethod
    def _get_model(cls):
        """获取模型实例"""
        global _model
        if _model is None:
            raise ValueError(
                "LangChain model not initialized. "
                "Call LangChainUtils.initialize_model(api_key) first."
            )
        return _model

    @classmethod
    def create_prompt_template(cls, template: str):
        """创建提示模板"""
        _ensure_langchain()
        return ChatPromptTemplate.from_messages([
            ("system",
                "你是一个专业的教育内容生成专家。"
                "核心规则：你必须且只能围绕用户在消息中指定的主题来生成内容。"
                "绝对禁止将用户指定的主题替换为其他话题，即使你认为其他话题更合适。"
                "严格按照指定的JSON格式输出，不要包含任何JSON之外的解释文字、markdown标记或代码块标记。"
            ),
            ("human", template),
        ])

    @classmethod
    def execute_chain(cls, prompt_template, inputs: Dict[str, Any]) -> str:
        """执行链式调用 (同步)

        Returns:
            LLM 响应的文本内容
        """
        _ensure_langchain()
        model = cls._get_model()
        runnable = prompt_template | model
        logger.info("[LangChain] Calling DeepSeek API...")
        result = runnable.invoke(inputs)
        content = str(result.content) if hasattr(result, 'content') else str(result)
        logger.info("[LangChain] DeepSeek response (first 500 chars): %s", content[:500])
        return content

    # [已注释] execute_chain_async — 当前仅使用同步版本（预留 Phase 2 异步迁移）
    # @classmethod
    # async def execute_chain_async(cls, prompt_template, inputs: Dict[str, Any]) -> str:
    #     """执行链式调用 (异步)
    #
    #     Returns:
    #         LLM 响应的文本内容
    #     """
    #     _ensure_langchain()
    #     model = cls._get_model()
    #     runnable = prompt_template | model
    #     result = await runnable.ainvoke(inputs)
    #     return str(result.content) if hasattr(result, 'content') else str(result)

    @classmethod
    def try_parse_json(cls, text: str) -> Optional[Dict[str, Any]]:
        """尝试从 LLM 响应中解析 JSON

        支持从 markdown 代码块或纯文本中提取 JSON。
        """
        if not text:
            return None

        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown ```json ... ``` 代码块中提取
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试找到第一个 { 和最后一个 }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass

        return None

    # ═══════════════════════════════════════════════════════════
    #  ★ v2.1 NEW: ModelFactory 方法
    #    提供结构化输出、工具绑定、流式事件等高级功能
    #    旧方法 (create_prompt_template, execute_chain, try_parse_json) 保持不变
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def create_model_instance(cls, model_name: str = "deepseek-chat",
                              api_key: str = None, base_url: str = "https://api.deepseek.com",
                              temperature: float = 0.7):
        """[v2.1] 创建独立的 ChatModel 实例（不依赖全局单例）。

        与 initialize_model() 的区别:
          - initialize_model(): 设置全局 _model，供旧代码使用
          - create_model_instance(): 返回新实例，支持多模型并存

        Args:
            model_name: 模型名称
            api_key: API Key（可选，默认从环境变量读取）
            base_url: API 地址
            temperature: 温度参数

        Returns:
            ChatOpenAI 实例
        """
        import os
        _ensure_langchain()
        key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("LLM_API_KEY")
        return ChatOpenAI(
            model=model_name,
            api_key=key,
            base_url=base_url,
            temperature=temperature,
        )

    @classmethod
    def create_structured_chain(cls, prompt_template, output_schema, method: str = "json_mode"):
        """[v2.1] 创建带结构化输出的 Chain。

        使用 LangChain 的 with_structured_output() 自动处理:
          JSON Schema 注入 → LLM 输出 → JSON 解析 → Pydantic 校验 → 失败重试

        替代 v2.0 的手动 try_parse_json() + 正则提取流程。

        Args:
            prompt_template: ChatPromptTemplate 实例
            output_schema: Pydantic v2 BaseModel 类（如 ProfessorOutput）
            method: 结构化输出方式
              - "json_mode": 使用 response_format={"type": "json_object"}（DeepSeek 兼容）
              - "function_calling": 使用 tool calling（OpenAI 原生支持）

        Returns:
            Runnable: prompt_template | model.with_structured_output(output_schema)

        Usage:
            from ..schemas.professor import ProfessorOutput
            chain = LangChainUtils.create_structured_chain(prompt, ProfessorOutput)
            result: ProfessorOutput = chain.invoke({"topic": "..."})
        """
        _ensure_langchain()
        model = cls._get_model()
        return prompt_template | model.with_structured_output(output_schema, method=method)

    @classmethod
    def create_tool_agent_chain(cls, model, tools: list, system_prompt: str):
        """[v2.1] 创建带工具绑定的 Agent Chain（用于 ReAct 循环）。

        Agent 可以自动决策：何时调用工具、如何解释工具返回结果。

        Args:
            model: ChatModel 实例
            tools: @tool 装饰的函数列表
            system_prompt: 系统提示词

        Returns:
            Runnable chain

        Usage:
            from ..tools import academic_search_tool
            llm = LangChainUtils.create_model_instance()
            chain = LangChainUtils.create_tool_agent_chain(
                llm, [academic_search_tool],
                "你是一个学术研究助手，可以使用 academic_search 工具查找论文。"
            )
        """
        _ensure_langchain()
        from langchain_core.prompts import ChatPromptTemplate

        llm_with_tools = model.bind_tools(tools)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),  # ReAct 中间步骤
        ])
        return prompt | llm_with_tools

    @classmethod
    async def stream_events(cls, chain, inputs: dict):
        """[v2.1] 异步流式迭代 Chain 事件（用于 WebSocket 实时推送）。

        使用 LangChain 的 astream_events() API (v2)，产生细粒度事件:
          - on_llm_start / on_llm_end
          - on_tool_start / on_tool_end
          - on_chain_start / on_chain_end

        Args:
            chain: Runnable 实例
            inputs: Chain 输入 dict

        Yields:
            dict: LangChain 事件对象

        Usage:
            async for event in LangChainUtils.stream_events(chain, {"topic": "..."}):
                if event["event"] == "on_llm_end":
                    content = event["data"]["output"].content
        """
        async for event in chain.astream_events(inputs, version="v2"):
            yield event
