"""
LangChain集成工具类 - DeepSeek版本

需要安装 langchain-openai 和 langchain-core:
    pip install langchain-openai langchain-core
"""
import json
import re
import threading
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()  # 读取 .env 文件内容并写入系统环境变量

logger = logging.getLogger("edunexus.agents")

_model = None
_model_lock = threading.Lock()

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
    """LangChain工具类 (DeepSeek API)"""

    @classmethod
    def initialize_model(cls, api_key: str, model_name: str = "deepseek-chat", base_url: str = "https://api.deepseek.com") -> None:
        """初始化DeepSeek LangChain模型（线程安全）

        Args:
            api_key: DeepSeek API Key
            model_name: 模型名称，默认 deepseek-chat
                        可选: deepseek-chat, deepseek-reasoner
        """
        global _model
        _ensure_langchain()
        with _model_lock:
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

    @classmethod
    async def execute_chain_async(cls, prompt_template, inputs: Dict[str, Any]) -> str:
        """执行链式调用 (异步)

        Returns:
            LLM 响应的文本内容
        """
        _ensure_langchain()
        model = cls._get_model()
        runnable = prompt_template | model
        result = await runnable.ainvoke(inputs)
        return str(result.content) if hasattr(result, 'content') else str(result)

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
