"""
工具注册表 — Agent 可以通过注册表按名称获取工具实例
"""
from typing import Dict, Any
from .academic_search import AcademicSearchTool
from .markdown_generator import MarkdownGeneratorTool


class ToolRegistry:
    """工具注册表 — 集中管理所有工具实例"""

    def __init__(self):
        self._tools: Dict[str, Any] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        """注册默认工具"""
        self.register("academic_search", AcademicSearchTool())
        self.register("markdown_generator", MarkdownGeneratorTool())

    def register(self, name: str, tool: Any) -> None:
        """注册工具"""
        self._tools[name] = tool

    def get(self, name: str) -> Any:
        """获取工具实例"""
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Tool '{name}' not found in registry. Available: {list(self._tools.keys())}")
        return tool

    def list_tools(self) -> list:
        """列出所有注册的工具名称"""
        return list(self._tools.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._tools
