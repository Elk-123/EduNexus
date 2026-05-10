import asyncio
import json
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.database import get_db, AsyncSessionLocal
from app.core.websocket import ws_manager
from app.core.security import create_access_token
from app.core.config import settings
from jose import jwt, JWTError

from app.models.student import Student
from app.models.profile import StudentProfile
from app.models.factory import GenerationTask, GeneratedResource
from app.schemas.factory import GenerateRequest, TaskStatusResponse, ResourceResponse, AgentChatRequest, AgentChatResponse
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.content_generator import generator

router = APIRouter()
logger = logging.getLogger("edunexus.factory")

# 保持后台任务引用，防止被 GC
_background_tasks: set[asyncio.Task] = set()


@router.post("/generate")
async def generate_content(
    payload: GenerateRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """提交主题，创建生成任务，后台启动多智能体流水线"""
    task = GenerationTask(
        student_id=current_user.id,
        topic=payload.topic,
        status="running",
        agents_status={"manager": "running"},
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # 获取学生画像（如果有的话）
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == current_user.id)
    )
    profile_db = result.scalars().first()
    profile = profile_db.profile_data if profile_db else None

    # 后台异步执行流水线（使用独立DB会话，避免请求结束后会话关闭）
    task_id = str(task.id)
    student_id = current_user.id
    bg_task = asyncio.create_task(_safe_run_pipeline(task_id, student_id, profile))
    _background_tasks.add(bg_task)
    bg_task.add_done_callback(_background_tasks.discard)

    return {"task_id": task_id, "status": "running"}


async def _safe_run_pipeline(task_id: str, student_id, profile):
    """包装流水线执行，使用独立DB会话，捕获异常并更新任务状态"""
    async with AsyncSessionLocal() as db:
        try:
            print(f"[PIPELINE] Starting pipeline for task {task_id}")
            result = await db.execute(
                select(GenerationTask).where(GenerationTask.id == task_id)
            )
            task = result.scalars().first()
            if not task:
                print(f"[PIPELINE] Task {task_id} not found")
                return

            print(f"[PIPELINE] Task loaded, running pipeline for topic: {task.topic}")
            orchestrator = AgentOrchestrator(db)
            await orchestrator.run_pipeline(task, profile)
            await db.commit()
            print(f"[PIPELINE] Pipeline completed for task {task_id}")
        except Exception as e:
            print(f"[PIPELINE] Pipeline failed for task {task_id}: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()  # 清理失败流水线的脏状态
            try:
                result = await db.execute(
                    select(GenerationTask).where(GenerationTask.id == task_id)
                )
                task = result.scalars().first()
                if task:
                    task.status = "failed"
                    task.updated_at = datetime.utcnow()
                    await db.commit()
            except Exception as ex2:
                print(f"[PIPELINE] Failed to update task status: {ex2}")
            try:
                await ws_manager.broadcast(task_id, {"type": "error", "message": str(e)})
            except Exception:
                pass


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """查询生成任务状态"""
    result = await db.execute(
        select(GenerationTask).where(
            GenerationTask.id == task_id,
            GenerationTask.student_id == current_user.id,
        )
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.get("/resources/{task_id}", response_model=list[ResourceResponse])
async def get_task_resources(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取某任务的生成资源列表"""
    result = await db.execute(
        select(GeneratedResource).where(
            GeneratedResource.task_id == task_id,
            GeneratedResource.student_id == current_user.id,
        )
    )
    return result.scalars().all()


@router.post("/agent/{agent_id}/chat", response_model=AgentChatResponse)
async def chat_with_agent(
    agent_id: str,
    payload: AgentChatRequest,
    current_user: Student = Depends(deps.get_current_user),
):
    """与指定智能体对话"""
    valid_agents = {"professor", "architect", "examiner", "director", "hacker", "reviewer"}
    if agent_id not in valid_agents:
        raise HTTPException(status_code=400, detail=f"无效的智能体ID。可选: {', '.join(valid_agents)}")

    content = await generator.generate_for_agent(agent_id, payload.message)
    return AgentChatResponse(
        reply=f"关于「{payload.message}」，作为{agent_id}智能体，我认为：{json.dumps(content, ensure_ascii=False)[:500]}",
        agent_type=agent_id,
    )


@router.websocket("/stream/{task_id}")
async def stream_task(
    websocket: WebSocket,
    task_id: str,
    token: str = Query(...),
):
    """WebSocket 端点：实时推送智能体状态和日志"""
    # 验证 Token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=4001)
            return
    except JWTError:
        await websocket.close(code=4001)
        return

    await ws_manager.connect(task_id, websocket)
    try:
        while True:
            # 保持连接存活，接收客户端心跳
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(task_id, websocket)
    except Exception:
        ws_manager.disconnect(task_id, websocket)

