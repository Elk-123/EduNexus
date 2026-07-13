from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class GenerateRequest(BaseModel):
    topic: str = Field(..., example="梯度下降算法的几何解释")


class TaskStatusResponse(BaseModel):
    id: UUID
    topic: str
    status: str
    agents_status: dict
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceResponse(BaseModel):
    id: UUID
    task_id: UUID
    agent_type: str
    resource_type: str
    content: dict
    status: str

    class Config:
        from_attributes = True


class AgentChatRequest(BaseModel):
    message: str
    task_id: Optional[str] = None   # 关联的 pipeline 任务ID（v1 UUID 或 v2 task_xxx）
    context: Optional[str] = None   # 前端传递的上下文（pipeline 已生成的内容摘要）


class AgentChatResponse(BaseModel):
    reply: str
    agent_type: str
