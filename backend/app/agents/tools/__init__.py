"""
Agent 工具集模块

v2.1 更新: 新增 LangChain @tool 装饰器版本的工具函数，
          可由 Agent 通过 model.bind_tools() 直接绑定调用。
"""
from .academic_search import AcademicSearchTool, AcademicSearchResult, academic_search_tool
from .markdown_generator import MarkdownGeneratorTool
from .web_search import web_search_tool
from .code_executor import code_executor_tool

__all__ = [
    # 原有类（向后兼容）
    "AcademicSearchTool",
    "AcademicSearchResult",
    "MarkdownGeneratorTool",
    # @tool 版本（供 LangChain/LangGraph Agent 绑定）
    "academic_search_tool",
    "web_search_tool",
    "code_executor_tool",
]
