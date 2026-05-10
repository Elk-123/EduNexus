from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.student import Student
from app.models.profile import StudentProfile
from app.models.graph import KnowledgeGraph
from app.schemas.graph import PathPlanRequest, PathPlanResponse, KnowledgeGraphResponse, KnowledgeNodeSchema, KnowledgeEdgeSchema, NodeResourcesResponse
from app.services.path_planner import planner

router = APIRouter()


@router.post("/plan", response_model=PathPlanResponse)
async def plan_learning_path(
    payload: PathPlanRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """根据学习目标生成个性化学习路径"""
    # 获取学生画像
    profile = None
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == current_user.id)
    )
    profile_db = result.scalars().first()
    if profile_db:
        profile = profile_db.profile_data

    # 调用 AI 规划
    plan_data = await planner.plan_path(payload.goal, profile)

    # 存入数据库
    kg = KnowledgeGraph(
        student_id=current_user.id,
        title=plan_data["title"],
        nodes=plan_data["nodes"],
        edges=plan_data["edges"],
        analysis_summary=plan_data.get("analysis_summary", ""),
        version=1,
    )
    db.add(kg)
    await db.commit()
    await db.refresh(kg)

    return PathPlanResponse(
        graph_id=kg.id,
        title=kg.title,
        nodes=[KnowledgeNodeSchema(**n) for n in kg.nodes],
        edges=[KnowledgeEdgeSchema(**e) for e in kg.edges],
        analysis_summary=kg.analysis_summary or "",
    )


@router.get("/{course_id}", response_model=KnowledgeGraphResponse)
async def get_graph(
    course_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取指定课程的最新知识图谱"""
    result = await db.execute(
        select(KnowledgeGraph)
        .where(KnowledgeGraph.student_id == current_user.id)
        .where(KnowledgeGraph.course_id == course_id)
        .order_by(KnowledgeGraph.version.desc())
        .limit(1)
    )
    kg = result.scalars().first()
    if not kg:
        raise HTTPException(status_code=404, detail="未找到该课程的学习路径")
    return KnowledgeGraphResponse(
        id=kg.id,
        course_id=kg.course_id,
        title=kg.title,
        nodes=[KnowledgeNodeSchema(**n) for n in kg.nodes],
        edges=[KnowledgeEdgeSchema(**e) for e in kg.edges],
        version=kg.version,
    )


@router.get("/path/{student_id}", response_model=KnowledgeGraphResponse)
async def get_personalized_path(
    student_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取指定学生的个性化学习路径（最新版本）"""
    result = await db.execute(
        select(KnowledgeGraph)
        .where(KnowledgeGraph.student_id == student_id)
        .order_by(KnowledgeGraph.created_at.desc())
        .limit(1)
    )
    kg = result.scalars().first()
    if not kg:
        raise HTTPException(status_code=404, detail="未找到该学生的学习路径")
    return KnowledgeGraphResponse(
        id=kg.id,
        course_id=kg.course_id,
        title=kg.title,
        nodes=[KnowledgeNodeSchema(**n) for n in kg.nodes],
        edges=[KnowledgeEdgeSchema(**e) for e in kg.edges],
        version=kg.version,
    )


@router.get("/node/{node_id}/resources", response_model=NodeResourcesResponse)
async def get_node_resources(
    node_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取某知识节点关联的学习资源"""
    # 查询与该节点标签匹配的生成资源
    from app.models.factory import GeneratedResource

    result = await db.execute(
        select(GeneratedResource)
        .where(GeneratedResource.student_id == current_user.id)
        .order_by(GeneratedResource.created_at.desc())
        .limit(20)
    )
    all_resources = result.scalars().all()

    resources_list = [
        {
            "id": str(r.id),
            "agent_type": r.agent_type,
            "resource_type": r.resource_type,
            "content": r.content,
            "status": r.status,
        }
        for r in all_resources
    ]

    return NodeResourcesResponse(node_id=node_id, resources=resources_list)
