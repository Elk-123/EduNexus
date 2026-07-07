import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.factory import GenerationTask, GeneratedResource
from app.schemas.profile import ProfileDimensions
# from app.services.content_generator import generator  # 避免循环导入，在函数内部导入
from app.core.websocket import ws_manager

logger = logging.getLogger("edunexus.orchestrator")

AGENT_DEFS = [
    {"id": "professor", "name": "教授智能体", "role": "Professor", "resource_type": "document"},
    {"id": "architect", "name": "架构师智能体", "role": "Architect", "resource_type": "mindmap"},
    {"id": "examiner", "name": "考官智能体", "role": "Examiner", "resource_type": "quiz"},
    {"id": "director", "name": "导演智能体", "role": "Director", "resource_type": "video_script"},
    {"id": "hacker", "name": "极客智能体", "role": "Hacker", "resource_type": "code_lab"},
]


class AgentOrchestrator:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ═══════════════════════════════════════════════════════════
    #  [已注释] v1.0 run_pipeline — 保留兼容，改用 run_v2_pipeline
    # ═══════════════════════════════════════════════════════════
    # async def run_pipeline(self, task: GenerationTask, profile=None):
    #     """[v1.0] 执行多智能体流水线"""
    #     ... (旧代码保留，不再使用)

    async def run_v2_pipeline(self, task: GenerationTask, profile=None):
        """[v2.0] 使用 agents/ 文件夹的新 AgentCoordinator 执行管道"""
        from app.agents import (
            AgentCoordinator, LangChainUtils,
            ManagerAgent, ProfessorAgent, ArchitectAgent,
            ExaminerAgent, DirectorAgent, HackerAgent, ReviewerAgent,
            MarkdownGeneratorTool,
        )
        from app.core.config import settings
        import os

        task_id = str(task.id)
        topic = task.topic

        # 初始化 DeepSeek
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', None) or os.getenv('DEEPSEEK_API_KEY')
        if api_key:
            LangChainUtils.initialize_model(api_key, 'deepseek-chat')

        # 创建协调器
        coord = AgentCoordinator()
        coord.register_agent(ManagerAgent())
        coord.register_agent(ProfessorAgent())
        coord.register_agent(ArchitectAgent())
        coord.register_agent(ExaminerAgent())
        coord.register_agent(DirectorAgent())
        coord.register_agent(HackerAgent())
        coord.register_agent(ReviewerAgent())

        # 捕获主线程 event loop（线程池中 get_event_loop() 会失败）
        main_loop = asyncio.get_running_loop()

        # 广播包装
        agent_names = {
            "manager": "Manager", "professor": "Professor", "architect": "Architect",
            "examiner": "Examiner", "director": "Director", "hacker": "Hacker",
            "reviewer": "Reviewer",
        }
        original_execute = {}
        for aid, agent in coord.agents.items():
            original_execute[aid] = agent.execute

            def make_wrapper(aid, orig_fn, loop):
                def wrapper(context):
                    name = agent_names.get(aid, aid)
                    # running
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast(task_id, {
                            "type": "agent_status", "agent": name, "status": "running",
                            "timestamp": datetime.utcnow().isoformat(),
                        }), loop
                    )
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast(task_id, {
                            "type": "agent_log", "agent": name,
                            "message": f"开始执行 {name}...", "type": "info",
                            "timestamp": datetime.utcnow().isoformat(),
                        }), loop
                    )
                    result = orig_fn(context)
                    status = "success" if result.status.value == "success" else "error"
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast(task_id, {
                            "type": "agent_status", "agent": name, "status": status,
                            "timestamp": datetime.utcnow().isoformat(),
                        }), loop
                    )
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast(task_id, {
                            "type": "agent_log", "agent": name,
                            "message": "完成 ✓" if status == "success" else f"失败: {result.error}",
                            "type": status, "timestamp": datetime.utcnow().isoformat(),
                        }), loop
                    )
                    return result
                return wrapper
            agent.execute = make_wrapper(aid, original_execute[aid], main_loop)

        # 在线程池中执行同步管道
        result = await main_loop.run_in_executor(None, coord.execute_pipeline, topic)

        # 恢复原始 execute
        for aid, agent in coord.agents.items():
            agent.execute = original_execute[aid]

        # 保存资源到数据库
        for r in result["results"]:
            if r.status.value == "success" and r.result:
                agent_def = next((d for d in AGENT_DEFS if d["id"] == r.agent_id), None)
                resource_type = agent_def["resource_type"] if agent_def else r.result.type
                if r.agent_id == "manager":
                    resource_type = "task_plan"
                elif r.agent_id == "reviewer":
                    resource_type = "review_report"

                resource = GeneratedResource(
                    task_id=task.id,
                    student_id=task.student_id,
                    agent_type=r.agent_id,
                    resource_type=resource_type,
                    content=r.result.content,
                    status="completed",
                )
                self.db.add(resource)

        # 生成 Markdown
        md_report = MarkdownGeneratorTool().generate_combined(result["accumulated_context"])

        task.status = "completed"
        task.updated_at = datetime.utcnow()
        await self.db.commit()

        await ws_manager.broadcast(task_id, {
            "type": "task_complete", "taskId": task_id, "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
        })
        await ws_manager.broadcast(task_id, {
            "type": "v2_result",
            "results": [{"agent_id": r.agent_id, "status": r.status.value, "duration": r.duration} for r in result["results"]],
            "accumulated_context": result["accumulated_context"],
            "markdown_report": md_report,
            "timestamp": datetime.utcnow().isoformat(),
        })

        logger.info("[V2] Pipeline completed: %s", task_id)

    async def _update_agent_status(self, task: GenerationTask, agent_id: str, status: str):
        current = dict(task.agents_status or {})
        current[agent_id] = status
        task.agents_status = current

    async def _broadcast(self, task_id: str, event_type: str, payload: dict):
        payload["type"] = event_type
        payload["timestamp"] = datetime.utcnow().isoformat()
        try:
            await ws_manager.broadcast(task_id, payload)
        except Exception as e:
            logger.warning(f"WebSocket broadcast failed: {e}")
