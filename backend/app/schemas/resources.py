from pydantic import BaseModel, Field
from typing import Optional, Union
from uuid import UUID


class TodayResourceResponse(BaseModel):
    id: Union[UUID, str]
    resource_type: str   # video | document | code | quiz
    title: str
    description: str = ""
    status: str = "current"  # completed | current | locked
    ai_reason: Optional[str] = None
    duration: str = ""
    url: Optional[str] = None  # 点击跳转链接

    class Config:
        from_attributes = True


class ResourceDetailResponse(BaseModel):
    id: UUID
    agent_type: str
    resource_type: str
    content: dict
    status: str


class ProgressUpdateRequest(BaseModel):
    status: str = "completed"   # not_started | in_progress | completed
    progress_percentage: float = 100.0
    time_spent: int = 0


class TrendingItem(BaseModel):
    source: str
    title: str
    meta: str
    tag: str
    url: str  # 点击跳转链接
