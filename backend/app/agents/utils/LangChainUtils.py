"""
LangChain集成工具类
"""
import os
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.messages import HumanMessage, SystemMessage

class LangChainUtils:
    """LangChain工具类"""

    _model = None

    @classmethod
    def initialize_model(cls, api_key: str, model_name: str = "gemini-2.5-flash") -> None:
        """初始化LangChain模型"""
        cls._model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
        )

    @classmethod
    def create_prompt_template(cls, template: str) -> ChatPromptTemplate:
        """创建提示模板"""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an expert assistant designed to help with educational content creation."),
            HumanMessage(content=template)
        ])

    @classmethod
    def create_runnable_sequence(cls, prompt_template: ChatPromptTemplate) -> RunnableSequence:
        """创建可运行序列"""
        if not cls._model:
            raise ValueError("LangChain model not initialized. Call LangChainUtils.initialize_model first.")

        return RunnableSequence.from_entries([
            prompt_template,
            cls._model
        ])

    @classmethod
    async def execute_chain(cls, prompt_template: ChatPromptTemplate, inputs: Dict[str, Any]) -> str:
        """执行链式调用"""
        if not cls._model:
            raise ValueError("LangChain model not initialized. Call LangChainUtils.initialize_model first.")

        runnable = cls.create_runnable_sequence(prompt_template)
        result = runnable.invoke(inputs)
        return str(result.content)