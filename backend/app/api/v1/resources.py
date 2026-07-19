from uuid import UUID
import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.student import Student
from app.models.factory import GeneratedResource
from app.schemas.resources import TodayResourceResponse, ResourceDetailResponse, ProgressUpdateRequest, TrendingItem

logger = logging.getLogger(__name__)
router = APIRouter()

# AI 主题固定内容（个人专属学习流 mock）
AI_RESOURCES = [
    {
        "id": "ai-1",
        "resource_type": "document",
        "title": "Large Language Models: A Survey",
        "description": "全面介绍大语言模型的发展历程、架构变体和未来方向，涵盖 Transformer 到 GPT-4 的演进",
        "status": "current",
        "ai_reason": "基于你的学习画像，推荐从 LLM 核心理论入手，为后续实践打基础",
        "duration": "20 min read",
        "url": "https://arxiv.org/abs/2302.07142"
    },
    {
        "id": "ai-2",
        "resource_type": "video",
        "title": "Transformer 架构深度解析",
        "description": "逐层讲解 Transformer 的 Self-Attention 机制、位置编码和多头注意力原理",
        "status": "completed",
        "ai_reason": "理解架构是实现高效推理的前提",
        "duration": "15 min",
        "url": "https://huggingface.co/learn/deep-rl-course/unit0/introduction"
    },
    {
        "id": "ai-3",
        "resource_type": "code",
        "title": "从零实现 Attention 机制",
        "description": "使用 PyTorch 手写一个简化的注意力模块，深入理解计算流程",
        "status": "completed",
        "ai_reason": "动手实践巩固理论知识",
        "duration": "25 min",
        "url": "https://github.com/huggingface/transformers"
    },
    {
        "id": "ai-4",
        "resource_type": "quiz",
        "title": "LLM 基础概念测试",
        "description": "测试你对 tokenization、context window、temperature 等核心概念的理解",
        "status": "completed",
        "ai_reason": "检验学习效果，查漏补缺",
        "duration": "10 min",
        "url": "https://huggingface.co/docs/transformers/en/index"
    },
]


# CS 行业热点 mock 数据
CS_TRENDING_FALLBACK = [
    {
        "source": "HackerNews",
        "title": "Rust 内存安全机制深度解析",
        "meta": "Top story · 856 points",
        "tag": "Systems",
        "url": "https://news.ycombinator.com/news"
    },
    {
        "source": "GitHub",
        "title": "vllm: 大模型推理性能提升 24 倍",
        "meta": "72k stars",
        "tag": "AI/ML",
        "url": "https://github.com/vllm-project/vllm"
    },
    {
        "source": "Arxiv",
        "title": "Mixture of Experts 前沿研究综述",
        "meta": "Hot in cs.LG",
        "tag": "Research",
        "url": "https://arxiv.org/list/cs.AI/recent"
    },
]


@router.get("/today", response_model=list[TodayResourceResponse])
async def get_today_resources(
    current_user: Student = Depends(deps.get_current_user),
):
    """获取当前学生的今日推送资源（AI 主题固定）"""
    # 直接返回固定 AI 主题内容
    return [
        TodayResourceResponse(**item)
        for item in AI_RESOURCES
    ]


@router.get("/trending", response_model=list[TrendingItem])
async def get_trending(
    current_user: Student = Depends(deps.get_current_user),
):
    """获取 CS 行业热点，优先实时数据 → 不可用时回退 mock"""
    logger.info("Request '/trending' for student: %s", current_user.username)

    async def fetch_hn(session: aiohttp.ClientSession) -> list[TrendingItem]:
        """HackerNews Algolia API — 搜索近期高热度科技文章"""
        url = "https://hn.algolia.com/api/v1/search"
        try:
            async with session.get(
                url,
                params={
                    "query": "ai OR llm OR programming OR rust OR python",
                    "tags": "story",
                    "hitsPerPage": 3,
                },
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status != 200:
                    body = (await resp.text())[:200]
                    print(f"  [HN] HTTP {resp.status}: {body}")
                    return []
                data = await resp.json()
                hits = data.get("hits", [])
                if not hits:
                    print(f"  [HN] 200 OK 但 hits=0")
                items = []
                for hit in hits[:2]:
                    title = hit.get("title") or hit.get("url", "").split("/")[-1] or hit.get("objectID", "")
                    if len(title) > 60:
                        title = title[:57] + "..."
                    items.append(TrendingItem(
                        source="HackerNews",
                        title=title,
                        meta=f"{hit.get('points', 0)} points",
                        tag="Discussion",
                        url=hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    ))
                return items
        except asyncio.TimeoutError:
            print(f"  [HN] 超时 (5s): {url}")
        except aiohttp.ClientConnectorError as e:
            print(f"  [HN] 连接失败 (DNS/网络): {e}")
        except Exception as e:
            print(f"  [HN] 异常 ({type(e).__name__}): {e}")
        return []

    async def fetch_github(session: aiohttp.ClientSession) -> list[TrendingItem]:
        """GitHub Search API — 热门仓库（sort by stars）"""
        url = "https://api.github.com/search/repositories"
        try:
            async with session.get(
                url,
                params={
                    "q": "ai agent OR llm OR machine learning stars:>1000",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 3,
                },
                headers={"Accept": "application/vnd.github+json"},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status != 200:
                    body = (await resp.text())[:300]
                    print(f"  [GitHub] HTTP {resp.status}: {body}")
                    return []
                data = await resp.json()
                repos = data.get("items", [])
                if not repos:
                    print(f"  [GitHub] 200 OK 但 items=0 (total_count={data.get('total_count', '?')})")
                items = []
                for repo in repos[:2]:
                    items.append(TrendingItem(
                        source="GitHub",
                        title=repo.get("full_name", repo.get("name", "")),
                        meta=f"{repo.get('stargazers_count', 0):,} stars",
                        tag="Repository",
                        url=repo.get("html_url", ""),
                    ))
                return items
        except asyncio.TimeoutError:
            print(f"  [GitHub] 超时 (5s): {url}")
        except aiohttp.ClientConnectorError as e:
            print(f"  [GitHub] 连接失败 (DNS/网络): {e}")
        except Exception as e:
            print(f"  [GitHub] 异常 ({type(e).__name__}): {e}")
        return []

    async def fetch_arxiv(session: aiohttp.ClientSession) -> list[TrendingItem]:
        """Arxiv API — 最新 AI/ML 论文"""
        url = "https://export.arxiv.org/api/query"
        import re
        try:
            async with session.get(
                url,
                params={
                    "search_query": "cat:cs.AI OR cat:cs.LG",
                    "start": 0,
                    "max_results": 3,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                },
                timeout=aiohttp.ClientTimeout(total=8),
            ) as resp:
                if resp.status != 200:
                    body = (await resp.text())[:200]
                    print(f"  [Arxiv] HTTP {resp.status}: {body}")
                    return []
                xml_text = await resp.text()
                # 解析 <entry> 而不是 <feed> 根标题
                entries = re.findall(r"<entry>(.*?)</entry>", xml_text, re.DOTALL)
                if not entries:
                    print(f"  [Arxiv] 200 OK 但 XML 中无 <entry> 元素")
                    return []
                items = []
                for entry_xml in entries[:2]:
                    title_m = re.search(r"<title>(.*?)</title>", entry_xml, re.DOTALL)
                    if not title_m:
                        continue
                    title = title_m.group(1).replace("\n", " ").strip()
                    if len(title) > 60:
                        title = title[:57] + "..."
                    # 取第一个 author 作为 meta
                    author_m = re.search(r"<name>(.*?)</name>", entry_xml)
                    meta = f"by {author_m.group(1)}" if author_m else "cs.AI/LG"
                    # 取 arxiv id 构造链接
                    id_m = re.search(r"<id>(.*?)</id>", entry_xml)
                    paper_url = id_m.group(1).strip() if id_m else "https://arxiv.org/list/cs.AI/recent"
                    items.append(TrendingItem(
                        source="Arxiv",
                        title=title,
                        meta=meta[:40],
                        tag="Research",
                        url=paper_url,
                    ))
                if not items:
                    print(f"  [Arxiv] 200 OK 有 {len(entries)} 个 entry 但无有效标题")
                return items
        except asyncio.TimeoutError:
            print(f"  [Arxiv] 超时 (8s): {url}")
        except aiohttp.ClientConnectorError as e:
            print(f"  [Arxiv] 连接失败 (DNS/网络): {e}")
        except Exception as e:
            print(f"  [Arxiv] 异常 ({type(e).__name__}): {e}")
        return []

    # 并发请求三个数据源（总超时 ~6s）
    trending_items: list[TrendingItem] = []
    print(f"[trending] 开始并发请求 HN / GitHub / Arxiv ...")
    try:
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                fetch_hn(session),
                fetch_github(session),
                fetch_arxiv(session),
                return_exceptions=True,
            )
        hn_count = len(results[0]) if isinstance(results[0], list) else 0
        gh_count = len(results[1]) if isinstance(results[1], list) else 0
        ar_count = len(results[2]) if isinstance(results[2], list) else 0
        print(f"[trending] 外部 API 结果: HN={hn_count}条, GitHub={gh_count}条, Arxiv={ar_count}条")
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                print(f"[trending] 数据源 {i} 异常: {r}")
            elif isinstance(r, list):
                trending_items.extend(r)
    except Exception as e:
        print(f"[trending] 聚合异常: {e}")
        logger.warning("Trending aggregator error: %s", e)

    # 外部数据不足 → 回退 mock
    if len(trending_items) < 3:
        print(f"[trending] 外部数据不足 ({len(trending_items)}条)，使用 CS fallback 补齐")
        logger.info("外部 API 数据不足 (%d条)，使用 CS fallback 补齐", len(trending_items))
        for item in CS_TRENDING_FALLBACK:
            if len(trending_items) >= 5:
                break
            trending_items.append(TrendingItem(**item))

    print(f"[trending] 最终返回 {len(trending_items)} 条")
    logger.info("Trending 返回 %d 条", len(trending_items))
    return trending_items


@router.get("/{resource_id}", response_model=ResourceDetailResponse)
async def get_resource_detail(
    resource_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取单个资源详情"""
    result = await db.execute(
        select(GeneratedResource).where(
            GeneratedResource.id == resource_id,
            GeneratedResource.student_id == current_user.id,
        )
    )
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="资源不存在")
    return ResourceDetailResponse(
        id=r.id,
        agent_type=r.agent_type,
        resource_type=r.resource_type,
        content=r.content or {},
        status=r.status,
    )


@router.put("/{resource_id}/progress")
async def update_resource_progress(
    resource_id: UUID,
    payload: ProgressUpdateRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """更新资源学习进度"""
    result = await db.execute(
        select(GeneratedResource).where(
            GeneratedResource.id == resource_id,
            GeneratedResource.student_id == current_user.id,
        )
    )
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="资源不存在")

    r.status = payload.status
    await db.commit()

    return {"message": "进度已更新", "resource_id": str(resource_id), "status": payload.status}


def _map_resource_type(rt: str) -> str:
    mapping = {
        "document": "document",
        "mindmap": "document",
        "quiz": "quiz",
        "video_script": "video",
        "code_lab": "code",
        "review_report": "document",
    }
    return mapping.get(rt, "document")
