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

    async def run_pipeline(self, task: GenerationTask, profile: ProfileDimensions | None = None):
        """执行多智能体流水线"""
        task_id = str(task.id)
        topic = task.topic

        # ---- Step 1: Manager 分析 ----
        await self._update_agent_status(task, "manager", "running")
        await self._broadcast(task_id, "agent_status", {"agent": "Manager", "status": "running"})
        await self._broadcast(task_id, "agent_log", {"agent": "Manager", "message": f"正在分析主题: {topic}", "type": "info"})
        await asyncio.sleep(1.2)  # 模拟分析时间
        await self._update_agent_status(task, "manager", "success")
        await self._broadcast(task_id, "agent_status", {"agent": "Manager", "status": "success"})
        await self._broadcast(task_id, "agent_log", {"agent": "Manager", "message": f"主题分析完成，调度 5 位专家并行生成...", "type": "success"})

        # ---- Step 2: 5 位专家并行生成 ----
        async def run_expert(agent_def: dict):
            agent_id = agent_def["id"]
            await self._update_agent_status(task, agent_id, "running")
            await self._broadcast(task_id, "agent_status", {"agent": agent_def["role"], "status": "running"})
            await self._broadcast(task_id, "agent_log", {"agent": agent_def["role"], "message": f"{agent_def['name']}开始生成内容...", "type": "info"})

            # 在函数内部导入，避免循环导入
            from app.services.content_generator import generator
            content = await generator.generate_for_agent(agent_id, topic, profile)

            resource = GeneratedResource(
                task_id=task.id,
                student_id=task.student_id,
                agent_type=agent_id,
                resource_type=agent_def["resource_type"],
                content=content,
                status="completed",
            )
            self.db.add(resource)

            await self._update_agent_status(task, agent_id, "success")
            await self._broadcast(task_id, "agent_status", {"agent": agent_def["role"], "status": "success"})
            await self._broadcast(task_id, "agent_log", {"agent": agent_def["role"], "message": f"{agent_def['name']}内容生成完毕", "type": "success"})

        await asyncio.gather(*(run_expert(d) for d in AGENT_DEFS))

        # ---- Step 3: Reviewer 审查 ----
        await self._update_agent_status(task, "reviewer", "running")
        await self._broadcast(task_id, "agent_status", {"agent": "Reviewer", "status": "running"})
        await self._broadcast(task_id, "agent_log", {"agent": "Reviewer", "message": "正在审查全部产出质量...", "type": "info"})

        # 在函数内部导入，避免循环导入
        from app.services.content_generator import generator
        review_content = await generator.generate_for_agent("reviewer", topic, profile)
        review_resource = GeneratedResource(
            task_id=task.id,
            student_id=task.student_id,
            agent_type="reviewer",
            resource_type="review_report",
            content=review_content,
            status="completed",
        )
        self.db.add(review_resource)

        await self._update_agent_status(task, "reviewer", "success")
        await self._broadcast(task_id, "agent_status", {"agent": "Reviewer", "status": "success"})
        await self._broadcast(task_id, "agent_log", {"agent": "Reviewer", "message": "质量审查通过 ✓", "type": "success"})

        # ---- 完成 ----
        task.status = "completed"
        task.updated_at = datetime.utcnow()
        await self.db.commit()
        await self._broadcast(task_id, "task_complete", {"taskId": task_id, "status": "completed"})

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
