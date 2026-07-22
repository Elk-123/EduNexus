"""
Web 搜索工具 — v2.3: DuckDuckGoSearchAPIWrapper (免费, 无需 API Key)
Tavily 实现注释保留，备后续切换。
"""
import logging

logger = logging.getLogger("edunexus.agents")

_langchain_web_search = None


def get_web_search():
    """获取 web_search 工具实例（DuckDuckGo → fallback）"""
    global _langchain_web_search
    if _langchain_web_search is not None:
        return _langchain_web_search

    try:
        from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
        from langchain_core.tools import tool as _t

        _ddg = DuckDuckGoSearchAPIWrapper()

        @_t
        def web_search(query: str) -> str:
            """Search the web. Returns structured results with title, snippet, and link."""
            try:
                results = _ddg.results(query[:300], max_results=5)
            except Exception:
                return f"Search failed for: {query}"
            if not results:
                return f"No results for: {query}"
            lines = []
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. {r.get('title', '')}\n   {r.get('snippet', '')}\n   {r.get('link', '')}")
            return "\n\n".join(lines)

        _langchain_web_search = web_search
        logger.info("[v2.3] web_search → DuckDuckGoSearchAPIWrapper")
        return _langchain_web_search

    except ImportError:
        _langchain_web_search = _build_fallback_tool()
        logger.info("[v2.3] web_search → fallback")
        return _langchain_web_search


def _build_fallback_tool():
    from langchain_core.tools import tool as _tool_dec

    @_tool_dec
    def web_search(query: str) -> str:
        """Search the web."""
        return f"Web search: '{query}'\n[提示] 搜索后端未配置（pip install duckduckgo-search langchain-community）"
    return web_search


web_search_tool = get_web_search()


# ═══════════════════════════════════════════════════════════════
#  [备选] Tavily Search API — 专为 AI Agent 设计，结果质量更高
#  切换方式: 取消注释 + pip install tavily-python
#  API Key: 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
# ═══════════════════════════════════════════════════════════════
#
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "tvly-dev-...")
#
# def get_web_search():
#     global _langchain_web_search
#     if _langchain_web_search is not None:
#         return _langchain_web_search
#     try:
#         from tavily import TavilyClient
#         from langchain_core.tools import tool as _t
#         _tavily = TavilyClient(api_key=TAVILY_API_KEY)
#
#         @_t
#         def web_search(query: str) -> str:
#             """Search the web. Returns filtered, high-quality results."""
#             response = _tavily.search(query=query[:400], max_results=8,
#                                       search_depth="advanced", include_raw_content=False)
#             results = response.get("results", [])
#             if not results:
#                 return f"No results for: {query}"
#             MIN_SCORE, MAX_LEN = 0.6, 400
#             JUNK = ["会员服务协议", "隐私政策", "用户协议", "© 版权所有",
#                      " subscribers", " views\n", "Posted: "]
#             lines, count = [], 0
#             for r in results:
#                 if count >= 5: break
#                 if r.get("score", 0) < MIN_SCORE: continue
#                 t, c, u = (r.get(k, "") or "").strip() for k in ("title", "content", "url")
#                 if any(p in t + c for p in JUNK): continue
#                 if len(c) > MAX_LEN: c = c[:MAX_LEN] + "..."
#                 count += 1
#                 lines.append(f"{count}. {t}  (相关度: {r.get('score',0):.0%})\n   {c}\n   {u}")
#             return "\n\n".join(lines) if lines else f"No quality results for: {query}"
#
#         _langchain_web_search = web_search
#         return _langchain_web_search
#     except ImportError:
#         ...  # 降级 DuckDuckGo
