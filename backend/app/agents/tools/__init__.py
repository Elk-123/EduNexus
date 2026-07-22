"""
Agent 工具集模块 — v2.3: LangChain 内置工具优先

- academic_search   → ArxivQueryRun (langchain_community)
- web_search        → DuckDuckGoSearchRun (langchain_community)
- code_executor     → 自实现 StructuredTool (subprocess 沙箱)
- markdown_generator → 自实现 (v1.0 兼容，agent_orchestrator 使用)
"""
from .academic_search import academic_search_tool, get_academic_search
from .web_search import web_search_tool, get_web_search
from .youtube_search import youtube_search_tool, get_youtube_search
from .code_executor import code_executor_tool, get_code_executor
from .markdown_generator import MarkdownGeneratorTool

__all__ = [
    "academic_search_tool", "web_search_tool", "youtube_search_tool",
    "code_executor_tool", "MarkdownGeneratorTool",
    "get_academic_search", "get_web_search", "get_youtube_search",
    "get_code_executor",
]
