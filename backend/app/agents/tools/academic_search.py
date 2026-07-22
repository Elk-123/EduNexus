"""
学术检索工具 — 对接 ArXiv API 获取真实学术文献

v2.1 更新: 新增 @tool 装饰器包装函数，可由 LangChain/LangGraph Agent 直接绑定调用。
          原有 AcademicSearchTool 类保留不变，保证向后兼容。

使用方式 (Agent 绑定工具):
    from .tools.academic_search import academic_search_tool
    agent = model.bind_tools([academic_search_tool])
"""
import logging
import xml.etree.ElementTree as ET
from typing import List, Optional
from dataclasses import dataclass, field
import httpx

logger = logging.getLogger("edunexus.agents")


@dataclass
class AcademicSearchResult:
    """学术检索结果"""
    title: str
    url: str
    snippet: str
    authors: List[str] = field(default_factory=list)
    year: Optional[str] = None
    source: str = "arxiv"


class AcademicSearchTool:
    """学术检索工具 — 通过 ArXiv API 搜索论文 (原 v2.0 实现，保持不变)"""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, timeout: float = 10.0):
        self._client = httpx.Client(timeout=timeout)
        self._async_client: Optional[httpx.AsyncClient] = None

    async def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=10.0)
        return self._async_client

    def search(self, query: str, max_results: int = 5) -> List[AcademicSearchResult]:
        """同步搜索学术文献"""
        try:
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending",
            }
            response = self._client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return self._parse_response(response.text)
        except Exception as e:
            logger.warning("ArXiv search failed for '%s': %s", query, e)
            return self._fallback(query)

    async def search_async(self, query: str, max_results: int = 5) -> List[AcademicSearchResult]:
        """异步搜索学术文献"""
        try:
            client = await self._get_async_client()
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending",
            }
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return self._parse_response(response.text)
        except Exception as e:
            logger.warning("ArXiv async search failed for '%s': %s", query, e)
            return self._fallback(query)

    def _parse_response(self, xml_text: str) -> List[AcademicSearchResult]:
        """解析 ArXiv Atom XML 响应"""
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
        root = ET.fromstring(xml_text)
        results = []

        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            link_el = entry.find("atom:id", ns)
            published_el = entry.find("atom:published", ns)

            authors = [
                (author.find("atom:name", ns).text or "")
                for author in entry.findall("atom:author", ns)
                if author.find("atom:name", ns) is not None
            ]

            title_text = title_el.text.strip() if title_el is not None and title_el.text else "Untitled"
            summary_text = summary_el.text.strip()[:300] if summary_el is not None and summary_el.text else ""
            url_text = link_el.text.strip() if link_el is not None and link_el.text else ""
            year = published_el.text[:4] if published_el is not None and published_el.text else None

            results.append(AcademicSearchResult(
                title=title_text,
                url=url_text,
                snippet=summary_text,
                authors=authors,
                year=year,
            ))

        return results[:5] if results else self._fallback("")

    def _fallback(self, query: str) -> List[AcademicSearchResult]:
        """当 API 不可用时的回退结果"""
        return [
            AcademicSearchResult(
                title=f"Search: {query}" if query else "No results",
                url="https://arxiv.org/search/?query=" + (query or ""),
                snippet="ArXiv API temporarily unavailable. Please try again later.",
                authors=["N/A"],
                year=None,
            )
        ]

    def close(self) -> None:
        """关闭 HTTP 客户端"""
        self._client.close()


# ═══════════════════════════════════════════════════════════════
#  ★ NEW: LangChain @tool 装饰器包装
#     Agent 可通过 model.bind_tools([academic_search_tool]) 直接调用
#     LangChain 自动处理 Tool Call → 函数调用 → 结果注入的整个 ReAct 循环
# ═══════════════════════════════════════════════════════════════

# 延迟导入避免 langchain_core 未安装时报错
_tool_available = False
try:
    from langchain_core.tools import tool as _tool_decorator
    _tool_available = True
except ImportError:
    _tool_available = False


def _create_academic_search_tool():
    """创建 LangChain @tool 包装函数（延迟创建，复用现有 AcademicSearchTool 逻辑）"""
    if not _tool_available:
        return None

    _search_tool_instance = AcademicSearchTool()

    @_tool_decorator
    def academic_search(query: str, max_results: int = 5) -> str:
        """搜索 ArXiv 学术论文数据库。

        当需要查找学术文献、研究论文、或验证某个技术概念的学术来源时使用此工具。
        返回论文标题、作者、年份和摘要。

        Args:
            query: 搜索关键词（英文效果最佳），如 "transformer attention mechanism"
            max_results: 返回结果数量，默认 5 篇
        """
        results = _search_tool_instance.search(query, max_results=max_results)
        if not results:
            return f"未找到与 '{query}' 相关的学术论文。"
        lines = []
        for i, r in enumerate(results, 1):
            authors = ", ".join(r.authors[:3])
            if len(r.authors) > 3:
                authors += " et al."
            year_str = f" ({r.year})" if r.year else ""
            lines.append(f"{i}. **{r.title}**{year_str}\n   Authors: {authors}\n   URL: {r.url}\n   {r.snippet[:200]}...")
        return "\n\n".join(lines)

    return academic_search


# 导出 @tool 版本 (如果 langchain_core 可用)
academic_search_tool = _create_academic_search_tool()
