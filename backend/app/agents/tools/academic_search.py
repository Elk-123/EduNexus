"""
学术检索工具 — v2.3: LangChain 内置 ArxivQueryRun
旧实现 (AcademicSearchTool + 手写 @tool) 见文件末尾注释。
"""
import os
import logging

logger = logging.getLogger("edunexus.agents")

_langchain_arxiv = None


def get_academic_search():
    """获取 academic_search 工具实例（自实现优先，ArxivQueryRun 作为备选）"""
    global _langchain_arxiv
    if _langchain_arxiv is not None:
        return _langchain_arxiv

    # 优先使用我们自己的实现（稳定，兼容 arxiv v2.x）
    _langchain_arxiv = _build_fallback_tool()
    logger.info("[v2.3] academic_search → custom @tool (ArXiv API)")

    # 未来切换 LangChain 内置: from langchain_community.tools.arxiv import ArxivQueryRun
    # 当前 ArxivQueryRun 与 arxiv v2.x 包不兼容 ('Search' object has no attribute 'results')
    return _langchain_arxiv


def _build_fallback_tool():
    """当 langchain_community 不可用时，用旧实现创建 @tool"""
    import xml.etree.ElementTree as ET
    from typing import List, Optional
    from dataclasses import dataclass, field
    import httpx

    @dataclass
    class AcademicSearchResult:
        title: str
        url: str
        snippet: str
        authors: List[str] = field(default_factory=list)
        year: Optional[str] = None
        source: str = "arxiv"

    class AcademicSearchTool:
        BASE_URL = "https://export.arxiv.org/api/query"

        def __init__(self, timeout: float = 5.0):
            proxy = os.environ.get("HTTPS_PROXY", "http://127.0.0.1:10809")
            self._client = httpx.Client(timeout=timeout, proxy=proxy)

        def search(self, query: str, max_results: int = 5):
            try:
                params = {"search_query": f"all:{query}", "start": 0,
                          "max_results": max_results, "sortBy": "relevance",
                          "sortOrder": "descending"}
                response = self._client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                return self._parse_response(response.text)
            except Exception as e:
                logger.warning("ArXiv search failed for '%s': %s", query, e)
                return self._fallback(query)

        def _parse_response(self, xml_text: str):
            ns = {"atom": "http://www.w3.org/2005/Atom",
                  "arxiv": "http://arxiv.org/schemas/atom"}
            root = ET.fromstring(xml_text)
            results = []
            for entry in root.findall("atom:entry", ns):
                title_el = entry.find("atom:title", ns)
                summary_el = entry.find("atom:summary", ns)
                link_el = entry.find("atom:id", ns)
                published_el = entry.find("atom:published", ns)
                authors = [author.find("atom:name", ns).text or ""
                          for author in entry.findall("atom:author", ns)
                          if author.find("atom:name", ns) is not None]
                results.append(AcademicSearchResult(
                    title=title_el.text.strip() if title_el is not None and title_el.text else "Untitled",
                    url=link_el.text.strip() if link_el is not None and link_el.text else "",
                    snippet=summary_el.text.strip()[:300] if summary_el is not None and summary_el.text else "",
                    authors=authors,
                    year=published_el.text[:4] if published_el is not None and published_el.text else None,
                ))
            return results[:5] if results else self._fallback("")

        def _fallback(self, query: str):
            return [AcademicSearchResult(
                title=f"Search: {query}" if query else "No results",
                url="https://arxiv.org/search/?query=" + (query or ""),
                snippet="ArXiv API temporarily unavailable.",
                authors=["N/A"], year=None,
            )]

        def close(self): self._client.close()

    _instance = AcademicSearchTool()
    from langchain_core.tools import tool as _tool_dec

    @_tool_dec
    def academic_search(query: str, max_results: int = 5) -> str:
        """Search ArXiv for academic papers. Input a research topic, returns paper titles, authors, and abstracts."""
        results = _instance.search(query, max_results=max_results)
        if not results:
            return f"No results for '{query}'."
        lines = []
        for i, r in enumerate(results, 1):
            authors = ", ".join(r.authors[:3])
            year_str = f" ({r.year})" if r.year else ""
            lines.append(f"{i}. **{r.title}**{year_str}\n   Authors: {authors}\n   URL: {r.url}\n   {r.snippet[:200]}...")
        return "\n\n".join(lines)

    return academic_search


# 模块导入时直接初始化（降级安全: ImportError → fallback）
academic_search_tool = get_academic_search()


# ═══════════════════════════════════════════════════════════════
#  [v2.2 legacy] 旧代码完全保留（注释），仅供参考
#  旧 AcademicSearchTool 类 + 旧 academic_search_tool @tool
#  已完整迁移至上方 _build_fallback_tool() 中的内联版本。
#  如需查看原始旧代码，见 git history: ea8a7c4 (7-22)
# ═══════════════════════════════════════════════════════════════
