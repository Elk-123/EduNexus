from uuid import UUID

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
    """获取行业热点（初期返回静态数据，后续可对接外部 API）"""
    return [
        TrendingItem(
            source="GitHub",
            title="Meta-Llama-3.1-405B-Instruct 已经发布",
            meta="24.5k stars this week",
            tag="LLM",
        ),
        TrendingItem(
            source="StackOverflow",
            title="为什么 WebAssembly 在 2025 年变得如此重要？",
            meta="120+ new answers",
            tag="Wasm",
        ),
        TrendingItem(
            source="Arxiv",
            title="KAN: Kolmogorov-Arnold Networks 论文引起热议",
            meta="New Architecture",
            tag="Research",
        ),
    ]


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
