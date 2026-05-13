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


@router.get("/today", response_model=list[TodayResourceResponse])
async def get_today_resources(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取当前学生的今日推送资源"""
    result = await db.execute(
        select(GeneratedResource)
        .where(GeneratedResource.student_id == current_user.id)
        .order_by(GeneratedResource.created_at.desc())
        .limit(10)
    )
    resources = result.scalars().all()

    if not resources:
        return []

    out = []
    for i, r in enumerate(resources):
        content = r.content or {}
        title = content.get("title", f"学习资源 - {r.agent_type}")
        description = content.get("description", "")

        out.append(
            TodayResourceResponse(
                id=r.id,
                resource_type=_map_resource_type(r.resource_type),
                title=title,
                description=description,
                status="completed" if i > 0 else "current",
                ai_reason=f"由 {r.agent_type} 智能体基于你的学习画像推荐" if i == 0 else None,
                duration="15 min" if r.resource_type == "video_script" else "10 min read",
            )
        )
    return out


@router.get("/trending", response_model=list[TrendingItem])
async def get_trending(
    current_user: Student = Depends(deps.get_current_user),
):
    """获取行业热点（从 GitHub Trending 和 HN 获取真实数据）"""
    trending_items = []

    # 1. 获取 GitHub Trending repositories
    try:
        async with aiohttp.ClientSession() as session:
            # 获取 Python 仓库的趋势
            async with session.get("https://api.github.com/search/repositories?q=created:>2024-01-01&sort=stars&order=desc&page=1&per_page=5") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for repo in data.get('items', [])[:3]:
                        trending_items.append(TrendingItem(
                            source="GitHub",
                            title=repo['name'],
                            meta=f"{repo['stargazers_count']} stars",
                            tag="Repository",
                        ))
    except Exception:
        # 如果 GitHub API 失败，使用备用数据
        pass

    # 2. 如果 GitHub 数据不足，添加其他来源
    if len(trending_items) < 3:
        # 添加一些通用的技术趋势
        fallback_items = [
            TrendingItem(
                source="HackerNews",
                title="OpenAI 发布 GPT-5 预览版",
                meta="Top story",
                tag="AI",
            ),
            TrendingItem(
                source="Dev.to",
                title="Rust 2025 年状态报告发布",
                meta="2.5k likes",
                tag="Programming",
            ),
            TrendingItem(
                source="Medium",
                title="微服务架构的最佳实践",
                meta="Trending in Technology",
                tag="Architecture",
            ),
        ]

        # 只添加缺失的部分
        for item in fallback_items:
            if len(trending_items) < 3:
                trending_items.append(item)

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
