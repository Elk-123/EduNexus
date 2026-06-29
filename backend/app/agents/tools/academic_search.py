"""
学术检索工具 — 对接 ArXiv API 获取真实学术文献
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
    """学术检索工具 — 通过 ArXiv API 搜索论文"""

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
