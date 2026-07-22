"""
YouTube 视频搜索工具 — 专为 Director Agent 设计
走 V2Ray 代理 (127.0.0.1:10809) 访问 YouTube。
"""
import os
import json
import logging
import re
import urllib.request
import urllib.parse

logger = logging.getLogger("edunexus.agents")

PROXY_HOST = os.getenv("HTTPS_PROXY", "http://127.0.0.1:10809")
_youtube_tool = None


def _fetch_youtube_page(query: str, max_results: int = 5) -> str:
    """通过代理抓取 YouTube 搜索结果页 HTML"""
    qs = urllib.parse.urlencode({"search_query": query})
    url = f"https://www.youtube.com/results?{qs}"

    proxy_handler = urllib.request.ProxyHandler({
        "https": PROXY_HOST,
        "http": PROXY_HOST,
    })
    opener = urllib.request.build_opener(proxy_handler)
    opener.addheaders = [("User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")]
    req = urllib.request.Request(url)

    try:
        with opener.open(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        logger.warning("YouTube fetch failed: %s", e)
        raise


def _parse_videos(html: str, max_results: int = 5) -> list[dict]:
    """从 YouTube HTML 中提取视频信息"""
    # YouTube 把初始数据存在 ytInitialData JSON 里
    match = re.search(r'var ytInitialData\s*=\s*({.*?});</script>', html)
    if not match:
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    videos = []
    contents = (data.get("contents", {})
                .get("twoColumnSearchResultsRenderer", {})
                .get("primaryContents", {})
                .get("sectionListRenderer", {})
                .get("contents", [{}])[0]
                .get("itemSectionRenderer", {})
                .get("contents", []))

    for item in contents:
        renderer = item.get("videoRenderer")
        if not renderer:
            continue
        vid = renderer.get("videoId", "")
        if not vid:
            continue
        title = (renderer.get("title", {}) or {}).get("runs", [{}])[0].get("text", "Untitled")
        channel = ((renderer.get("ownerText", {}) or {}).get("runs", [{}])[0].get("text", "Unknown"))
        duration = (renderer.get("lengthText", {}) or {}).get("simpleText", "?")
        views = (renderer.get("viewCountText", {}) or {}).get("simpleText", "")
        thumb = ((renderer.get("thumbnail", {}) or {}).get("thumbnails", [{}])[0].get("url", ""))
        videos.append({
            "id": vid, "title": title, "channel": channel,
            "duration": duration, "views": views, "thumbnail": thumb,
            "url": f"https://www.youtube.com/watch?v={vid}",
        })
        if len(videos) >= max_results:
            break

    return videos


def get_youtube_search():
    """获取 YouTube 搜索工具实例"""
    global _youtube_tool
    if _youtube_tool is not None:
        return _youtube_tool

    from langchain_core.tools import tool as _t

    @_t
    def youtube_search(query: str) -> str:
        """Search YouTube for educational videos. Returns titles, channels, durations, and URLs.

        Use this to find real, existing videos for a video script.
        Input a topic or keywords in English for best results."""
        try:
            html = _fetch_youtube_page(query, max_results=5)
            results = _parse_videos(html, max_results=5)
        except Exception as e:
            return f"YouTube search failed: {e}"

        if not results:
            return f"No YouTube videos found for: {query}"

        lines = []
        for i, r in enumerate(results, 1):
            lines.append(
                f"{i}. {r['title']}\n"
                f"   频道: {r['channel']}  |  时长: {r['duration']}  |  {r['views']}\n"
                f"   缩略图: {r['thumbnail']}\n"
                f"   URL: {r['url']}"
            )
        return "\n\n".join(lines)

    _youtube_tool = youtube_search
    logger.info("[v2.3] youtube_search initialized (proxy: %s)", PROXY_HOST)
    return _youtube_tool


youtube_search_tool = get_youtube_search()
