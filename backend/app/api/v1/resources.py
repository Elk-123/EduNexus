from uuid import UUID
import aiohttp
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.student import Student
from app.models.factory import GeneratedResource
from app.schemas.resources import TodayResourceResponse, ResourceDetailResponse, ProgressUpdateRequest, TrendingItem

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
    """获取 CS 行业热点（HackerNews + GitHub + Arxiv）"""
    trending_items = []

    # 1. 尝试从 HackerNews Algolia API 获取最新科技讨论
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": "programming OR rust OR ai OR machine learning",
                    "tags": "story",
                    "hitsPerPage": 3
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for hit in data.get('hits', [])[:2]:
                        points = hit.get('points', 0)
                        trending_items.append(TrendingItem(
                            source="HackerNews",
                            title=hit.get('title', hit.get('url', '')).split('/')[-1][:40] or hit.get('objectID', ''),
                            meta=f"{points} points",
                            tag="Discussion",
                            url=hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                        ))
    except Exception:
        pass

    # 2. 尝试从 GitHub 获取热门仓库
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": "language:python OR language:rust OR language:go stars:>1000",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 2
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for repo in data.get('items', [])[:1]:
                        trending_items.append(TrendingItem(
                            source="GitHub",
                            title=repo['name'],
                            meta=f"{repo['stargazers_count']} stars",
                            tag="Repository",
                            url=repo['html_url'],
                        ))
    except Exception:
        pass

    # 3. 尝试从 Arxiv 获取最新 AI 论文
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://export.arxiv.org/api/query",
                params={
                    "search_query": "cat:cs.AI OR cat:cs.LG",
                    "start": 0,
                    "max_results": 1,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending"
                }
            ) as resp:
                if resp.status == 200:
                    xml_text = await resp.text()
                    import re
                    title_match = re.search(r'<title>(.*?)</title>', xml_text)
                    if title_match:
                        title = title_match.group(1).replace('\n', ' ').strip()
                        trending_items.append(TrendingItem(
                            source="Arxiv",
                            title=title[:50] + '...' if len(title) > 50 else title,
                            meta="Hot in cs.AI/LG",
                            tag="Research",
                            url="https://arxiv.org/list/cs.AI/recent",
                        ))
    except Exception:
        pass

    # 4. 如果数据不足，使用 CS 主题 fallback
    if len(trending_items) < 3:
        for item in CS_TRENDING_FALLBACK:
            if len(trending_items) < 3:
                trending_items.append(TrendingItem(**item))

    return trending_items[:3]  # 确保只返回 3 条


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
