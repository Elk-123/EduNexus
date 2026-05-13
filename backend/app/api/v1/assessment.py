from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api import deps
from app.models.student import Student
from app.models.factory import GeneratedResource, GenerationTask
from app.models.graph import KnowledgeGraph
from app.schemas.assessment import WeeklyReport, StatsData, HistoryRecord

router = APIRouter()


@router.get("/weekly", response_model=WeeklyReport)
async def get_weekly_report(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取周学情报告"""
    # 计算一周前的日期
    week_ago = datetime.now() - timedelta(days=7)

    # 1. 统计学习时长（根据资源创建时间估算）
    result = await db.execute(
        select(GeneratedResource)
        .where(
            GeneratedResource.student_id == current_user.id,
            GeneratedResource.created_at >= week_ago
        )
    )
    resources = result.scalars().all()

    # 估算学习时长（每个资源平均 15 分钟）
    study_minutes = len(resources) * 15
    study_hours = study_minutes / 60

    # 2. 完成课程数
    completed_tasks = await db.execute(
        select(GenerationTask)
        .where(
            GenerationTask.student_id == current_user.id,
            GenerationTask.status == "completed",
            GenerationTask.created_at >= week_ago
        )
    )
    completed_count = completed_tasks.scalar_count()

    # 3. 测验平均分（从资源中计算）
    quiz_resources = [r for r in resources if r.resource_type == "quiz"]
    average_score = 85  # 默认分数，实际应该从答题记录计算

    # 4. 知识点掌握率
    result = await db.execute(
        select(KnowledgeGraph)
        .where(
            KnowledgeGraph.student_id == current_user.id,
            KnowledgeGraph.created_at >= week_ago
        )
    )
    graphs = result.scalars().all()

    # 计算完成节点比例
    total_nodes = sum(len(graph.nodes) for graph in graphs) if graphs else 0
    completed_nodes = sum(
        sum(1 for node in graph.nodes if node.get("status") == "completed")
        for graph in graphs
    )
    mastery_rate = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0

    return WeeklyReport(
        study_hours=round(study_hours, 1),
        completed_courses=completed_count,
        average_score=average_score,
        knowledge_mastery=round(mastery_rate, 1),
        week_start=(datetime.now() - timedelta(days=7)).isoformat(),
        week_end=datetime.now().isoformat()
    )


@router.get("/stats", response_model=StatsData)
async def get_learning_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取学习统计数据（雷达图数据）"""
    # 获取最近 30 天的学习数据
    days_ago = datetime.now() - timedelta(days=30)

    # 1. 学科表现（根据资源类型统计）
    result = await db.execute(
        select(GeneratedResource)
        .where(
            GeneratedResource.student_id == current_user.id,
            GeneratedResource.created_at >= days_ago
        )
    )
    resources = result.scalars().all()

    # 按类型分组统计
    type_stats = {
        "数学": len([r for r in resources if "math" in r.agent_type.lower() or r.title.lower().contains("math")]),
        "物理": len([r for r in resources if "physics" in r.agent_type.lower() or r.title.lower().contains("physics")]),
        "编程": len([r for r in resources if r.resource_type == "code_lab" or "programming" in r.agent_type.lower()]),
        "英语": len([r for r in resources if "english" in r.agent_type.lower() or r.title.lower().contains("english")]),
        "逻辑": len([r for r in resources if "logic" in r.agent_type.lower() or "reasoning" in r.agent_type.lower()]),
        "创意": len([r for r in resources if "creative" in r.agent_type.lower() or r.resource_type == "mindmap"])
    }

    # 标准化到 0-100 范围
    max_count = max(type_stats.values()) if type_stats.values() else 1
    normalized_stats = {
        subject: min(int(count / max_count * 100), 100)
        for subject, count in type_stats.items()
    }

    # 2. 学习趋势
    result = await db.execute(
        select(func.date(GeneratedResource.created_at), func.count(GeneratedResource.id))
        .where(GeneratedResource.student_id == current_user.id)
        .where(GeneratedResource.created_at >= days_ago)
        .group_by(func.date(GeneratedResource.created_at))
        .order_by(func.date(GeneratedResource.created_at))
    )
    trend_data = result.all()

    return StatsData(
        subjects=list(normalized_stats.keys()),
        scores=list(normalized_stats.values()),
        trend=trend_data
    )


@router.get("/history", response_model=List[HistoryRecord])
async def get_history(
    limit: int = 10,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取学习历史记录"""
    result = await db.execute(
        select(GeneratedResource)
        .where(GeneratedResource.student_id == current_user.id)
        .order_by(GeneratedResource.created_at.desc())
        .limit(limit)
    )
    resources = result.scalars().all()

    # 转换为历史记录格式
    history = []
    for resource in resources:
        history.append(HistoryRecord(
            id=str(resource.id),
            title=resource.content.get("title", "学习资源") if resource.content else "未命名资源",
            type=resource.resource_type,
            completed_at=resource.created_at.isoformat(),
            score=resource.content.get("score", 0) if resource.content else 0,
            duration=estimate_duration(resource.resource_type)
        ))

    return history


def estimate_duration(resource_type: str) -> str:
    """估算资源学习时长"""
    duration_map = {
        "document": "10 min read",
        "video_script": "15 min video",
        "quiz": "5 min test",
        "code_lab": "20 min practice",
        "mindmap": "5 min review",
        "review_report": "8 min read"
    }
    return duration_map.get(resource_type, "10 min")