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

# ── v2.0 Agent 模块导入 ──────────────────────────────────────
from app.agents import (
    AgentCoordinator, LangChainUtils,
    ManagerAgent, ProfessorAgent, ArchitectAgent,
    ExaminerAgent, DirectorAgent, HackerAgent, ReviewerAgent,
    MarkdownGeneratorTool, ToolRegistry,
)

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
    # 使用generator创建任务
    result = await generator.generate_content(payload, current_user.id, db)

    # 获取学生画像（如果有的话）
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == current_user.id)
    )
    profile_db = profile_result.scalars().first()
    profile = profile_db.profile_data if profile_db else None

    # 后台异步执行流水线
    task_id = result["task_id"]
    bg_task = asyncio.create_task(_safe_run_pipeline(task_id, current_user.id, profile))
    _background_tasks.add(bg_task)
    bg_task.add_done_callback(_background_tasks.discard)

    return result


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

            print(f"[PIPELINE] Task loaded, running v2 pipeline for topic: {task.topic}")
            orchestrator = AgentOrchestrator(db)
            await orchestrator.run_v2_pipeline(task, profile)
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


@router.get("/simple-debug")
async def simple_debug():
    """最简单的调试端点"""
    return {"message": "Simple debug endpoint works"}
async def test_debug(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """调试端点"""
    print(f"[DEBUG] test-debug called for user: {current_user.id}")

    # 查看用户的所有任务
    result = await db.execute(
        select(GenerationTask).where(
            GenerationTask.student_id == current_user.id,
        ).order_by(GenerationTask.created_at.desc())
    )
    tasks = result.scalars().all()
    print(f"[DEBUG] User has {len(tasks)} tasks")

    if tasks:
        print(f"[DEBUG] Latest task ID: {tasks[0].id}, Status: {tasks[0].status}")
        return {"message": f"Found {len(tasks)} tasks", "latest_id": str(tasks[0].id)}
    else:
        return {"message": "No tasks found"}

@router.get("/latest", response_model=TaskStatusResponse)
async def get_latest_task(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取最新的生成任务"""
    from app.schemas.factory import TaskStatusResponse

    print(f"[DEBUG] /latest called for user: {current_user.id}")
    result = await db.execute(
        select(GenerationTask).where(
            GenerationTask.student_id == current_user.id,
        ).order_by(GenerationTask.created_at.desc()).limit(1)
    )
    task = result.scalars().first()
    print(f"[DEBUG] Found task: {task is not None}, task_id: {task.id if task else None}")
    if not task:
        print(f"[DEBUG] No task found for user {current_user.id}")
        # 查看该用户的所有任务
        all_result = await db.execute(
            select(GenerationTask).where(
                GenerationTask.student_id == current_user.id,
            )
        )
        all_tasks = all_result.scalars().all()
        print(f"[DEBUG] User has {len(all_tasks)} tasks total")
        raise HTTPException(status_code=404, detail="没有找到生成任务")

    # 手动构建响应对象
    response = TaskStatusResponse(
        id=task.id,
        topic=task.topic,
        status=task.status,
        agents_status=task.agents_status or {},
        created_at=task.created_at
    )

    print(f"[DEBUG] Returning response: {response}")
    return response


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """查询生成任务状态（兼容 v1 UUID 和 v2 字符串 task_id）"""
    # v2 任务：检查内存状态
    if task_id.startswith("task_"):
        status = _v2_task_status.get(task_id, "running")
        return {
            "id": task_id,
            "topic": "",
            "status": status,
            "agents_status": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

    # v1 任务：查数据库
    try:
        uid = UUID(task_id)
    except ValueError:
        # 非标准格式，按 v2 处理
        status = _v2_task_status.get(task_id, "running")
        return {
            "id": task_id,
            "topic": "",
            "status": status,
            "agents_status": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

    result = await db.execute(
        select(GenerationTask).where(
            GenerationTask.id == uid,
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
    db: AsyncSession = Depends(deps.get_db),
):
    """与指定智能体深度对话（基于 pipeline 上下文）

    支持两种上下文注入方式：
    1. payload.task_id — v1 任务：从 generated_resources 表加载该 agent 的已生成内容
    2. payload.context  — v2 任务 / 前端直接传递的上下文文本
    两者可同时提供，context 会追加到自动加载的内容之后。
    """
    valid_agents = {"professor", "architect", "examiner", "director", "hacker", "reviewer"}
    if agent_id not in valid_agents:
        raise HTTPException(status_code=400, detail=f"无效的智能体ID。可选: {', '.join(valid_agents)}")

    # ── 构建上下文 ──────────────────────────────────────────
    context_parts: list[str] = []

    # --- 方式1: 从 task_id 自动加载 ---
    if payload.task_id:
        try:
            uid = UUID(payload.task_id)
            # v1 任务：查询数据库
            result = await db.execute(
                select(GeneratedResource).where(
                    GeneratedResource.task_id == uid,
                    GeneratedResource.student_id == current_user.id,
                    GeneratedResource.agent_type == agent_id,
                )
            )
            db_resource = result.scalars().first()
            if db_resource and db_resource.content:
                context_parts.append(
                    f"[已生成内容] 你之前为任务 {payload.task_id} 生成了以下内容：\n"
                    f"{json.dumps(db_resource.content, ensure_ascii=False, indent=2)[:3000]}"
                )
        except ValueError:
            # v2 任务 (task_xxx) / 其他格式：数据库无记录，依赖前端传递 context
            if not payload.context:
                logger.warning(f"v2 task {payload.task_id} 无 DB 记录且未传递 context，对话将缺少上下文")

    # --- 方式2: 前端直接传递 ---
    if payload.context:
        context_parts.append(f"[上下文] {payload.context}")

    context = "\n\n".join(context_parts) if context_parts else ""

    # ── 调用对话方法（有上下文走 DeepSeek 对话，无上下文走生成） ──
    if context:
        result = await generator.chat_with_agent(agent_id, payload.message, context)
        return AgentChatResponse(
            reply=result["reply"],
            agent_type=result["agent_type"],
        )
    else:
        # 无上下文时回退到 generate_for_agent（保持向后兼容）
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


# ═══════════════════════════════════════════════════════════════
#  v2.0 Agent 端点（使用 agents/ 文件夹的新实现）
# ═══════════════════════════════════════════════════════════════

_v2_coordinator: AgentCoordinator | None = None
_v2_coordinator_lock = __import__('threading').Lock()
_v2_task_status: dict[str, str] = {}  # task_id → status (running/completed/failed)


def _get_v2_coordinator() -> AgentCoordinator:
    """获取或初始化 v2.0 AgentCoordinator 单例"""
    global _v2_coordinator
    if _v2_coordinator is not None:
        return _v2_coordinator

    with _v2_coordinator_lock:
        if _v2_coordinator is not None:
            return _v2_coordinator

        # 初始化 DeepSeek 模型
        from app.core.config import settings
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', None) or __import__('os').getenv('DEEPSEEK_API_KEY')
        if api_key:
            LangChainUtils.initialize_model(api_key, 'deepseek-chat')
            logger.info("[V2] DeepSeek model initialized")
        else:
            logger.warning("[V2] DEEPSEEK_API_KEY not set — agents will use fallback mode")

        _v2_coordinator = AgentCoordinator()
        _v2_coordinator.register_agent(ManagerAgent())
        _v2_coordinator.register_agent(ProfessorAgent())
        _v2_coordinator.register_agent(ArchitectAgent())
        _v2_coordinator.register_agent(ExaminerAgent())
        _v2_coordinator.register_agent(DirectorAgent())
        _v2_coordinator.register_agent(HackerAgent())
        _v2_coordinator.register_agent(ReviewerAgent())
        logger.info("[V2] AgentCoordinator initialized with 7 agents")

    return _v2_coordinator


@router.post("/generate-v2")
async def generate_v2(
    payload: GenerateRequest,
    current_user: Student = Depends(deps.get_current_user),
):
    """[v2.0] 使用新 Agent 引擎生成内容

    直接调用 AgentCoordinator 执行 7 Agent 管道，
    通过 WebSocket 实时推送状态，完成后返回完整结果。
    """
    topic = payload.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="主题不能为空")

    task_id = f"task_{__import__('uuid').uuid4().hex[:12]}"
    logger.info("[V2] Starting generation for topic: %s (task: %s)", topic, task_id)

    # 创建后台任务执行管道
    bg_task = asyncio.create_task(_run_v2_pipeline(task_id, topic))
    _background_tasks.add(bg_task)
    bg_task.add_done_callback(_background_tasks.discard)

    return {
        "task_id": task_id,
        "topic": topic,
        "status": "running",
        "message": "v2.0 Agent pipeline started",
    }


async def _run_v2_pipeline(task_id: str, topic: str):
    """后台执行 v2.0 Agent 管道，通过 WebSocket 广播进度"""
    _v2_task_status[task_id] = "running"
    coordinator = _get_v2_coordinator()
    agent_names = {
        "manager": "Manager", "professor": "Professor", "architect": "Architect",
        "examiner": "Examiner", "director": "Director", "hacker": "Hacker",
        "reviewer": "Reviewer",
    }

    try:
        # 广播开始
        await ws_manager.broadcast(task_id, {
            "type": "agent_log",
            "agent": "System",
            "message": f"🚀 v2.0 Agent 管道启动: {topic}",
            "type": "info",
            "timestamp": datetime.utcnow().isoformat(),
        })

        # 捕获主线程 event loop（线程池中 get_event_loop() 会失败）
        main_loop = asyncio.get_running_loop()

        # 自定义回调：每个 Agent 状态变化时广播
        original_execute = {}

        for agent_id, agent in coordinator.agents.items():
            original_execute[agent_id] = agent.execute

            def make_wrapper(aid, orig_fn, loop):
                def wrapper(context):
                    name = agent_names.get(aid, aid)
                    # 广播 running 状态
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast(task_id, {
                            "type": "agent_status",
                            "agent": name,
                            "status": "running",
                            "timestamp": datetime.utcnow().isoformat(),
                        }), loop
                    )
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast(task_id, {
                            "type": "agent_log",
                            "agent": name,
                            "message": f"开始执行 {name}...",
                            "type": "info",
                            "timestamp": datetime.utcnow().isoformat(),
                        }), loop
                    )

                    result = orig_fn(context)

                    # 广播结果
                    status = "success" if result.status.value == "success" else "error"
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast(task_id, {
                            "type": "agent_status",
                            "agent": name,
                            "status": status,
                            "timestamp": datetime.utcnow().isoformat(),
                        }), loop
                    )
                    msg = "完成 ✓" if status == "success" else f"失败: {result.error}"
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast(task_id, {
                            "type": "agent_log",
                            "agent": name,
                            "message": msg,
                            "type": status,
                            "timestamp": datetime.utcnow().isoformat(),
                        }), loop
                    )
                    return result
                return wrapper

            agent.execute = make_wrapper(agent_id, original_execute[agent_id], main_loop)

        # 执行管道（在线程池中运行同步代码）
        loop = main_loop
        result = await loop.run_in_executor(
            None, coordinator.execute_pipeline, topic
        )

        # 恢复原始 execute 方法
        for agent_id, agent in coordinator.agents.items():
            agent.execute = original_execute[agent_id]

        # 生成 Markdown 报告
        md_tool = MarkdownGeneratorTool()
        markdown_report = md_tool.generate_combined(result["accumulated_context"])

        # 广播完成
        _v2_task_status[task_id] = "completed"
        await ws_manager.broadcast(task_id, {
            "type": "task_complete",
            "taskId": task_id,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
        })
        await ws_manager.broadcast(task_id, {
            "type": "v2_result",
            "results": [
                {
                    "agent_id": r.agent_id,
                    "status": r.status.value,
                    "duration": r.duration,
                }
                for r in result["results"]
            ],
            "accumulated_context": result["accumulated_context"],
            "markdown_report": markdown_report,
            "timestamp": datetime.utcnow().isoformat(),
        })

        logger.info("[V2] Pipeline completed for task %s", task_id)

    except Exception as e:
        _v2_task_status[task_id] = "failed"
        logger.error("[V2] Pipeline failed for task %s: %s", task_id, e)
        import traceback
        traceback.print_exc()
        await ws_manager.broadcast(task_id, {
            "type": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        })

