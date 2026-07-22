"""
Web 搜索工具 — 互联网信息检索

[建议] 当前提供框架代码，具体实现取决于选择的搜索 API:
  - Tavily Search API (推荐，专为 AI Agent 设计): pip install tavily-python
  - DuckDuckGo (免费，无需 API key): pip install duckduckgo-search
  - SerpAPI / Brave Search / Google Custom Search

使用方式:
    from .tools.web_search import web_search_tool
    agent = model.bind_tools([web_search_tool])
"""
import logging

logger = logging.getLogger("edunexus.agents")

# 延迟导入
_tool_available = False
try:
    from langchain_core.tools import tool as _tool_decorator
    _tool_available = True
except ImportError:
    _tool_available = False


def _create_web_search_tool():
    """创建 Web 搜索 @tool"""
    if not _tool_available:
        return None

    @_tool_decorator
    def web_search(query: str) -> str:
        """搜索互联网获取最新信息。

        当需要查找最新资讯、教程、文档或 ArXiv 学术数据库之外的资料时使用此工具。
        适合 DirectorAgent 验证视频资源真实性和 HackerAgent 查找最新 API 文档。

        Args:
            query: 搜索关键词
        """
        # [建议] 方案 A: Tavily Search API（推荐）
        # from tavily import TavilyClient
        # client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        # response = client.search(query, search_depth="basic")
        # return json.dumps(response["results"], ensure_ascii=False, indent=2)

        # [建议] 方案 B: DuckDuckGo（免费，无需 API key）
        # from duckduckgo_search import DDGS
        # with DDGS() as ddgs:
        #     results = list(ddgs.text(query, max_results=5))
        # return "\n\n".join(
        #     f"{i}. **{r['title']}**\n   {r['body'][:200]}\n   {r['href']}"
        #     for i, r in enumerate(results, 1)
        # )

        logger.info("[WebSearch] Query: %s (backends not configured)", query)
        return (
            f"🔍 Web 搜索: '{query}'\n\n"
            "[提示] Web 搜索后端未配置。\n"
            "安装 Tavily: pip install tavily-python\n"
            "或 DuckDuckGo: pip install duckduckgo-search\n"
            "然后在 tools/web_search.py 中启用对应的搜索方案。"
        )

    return web_search


web_search_tool = _create_web_search_tool()
