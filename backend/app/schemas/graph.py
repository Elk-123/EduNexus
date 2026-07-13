from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class KnowledgeNodeSchema(BaseModel):
    id: str
    label: str
    type: str = "standard"   # standard | injected | milestone
    phase: int = 1            # 阶段编号 1/2/3
    proficiency: float = 0.5  # 0-1
    status: str = "pending"   # completed | active | pending


class KnowledgeEdgeSchema(BaseModel):
    source: str = Field(..., alias="from")
    target: str = Field(..., alias="to")
    isDynamic: bool = False

    class Config:
        populate_by_name = True


class PathPlanRequest(BaseModel):
    goal: str = Field(..., example="Transformer Architecture")


class PathPlanResponse(BaseModel):
    graph_id: UUID
    title: str
    nodes: list[KnowledgeNodeSchema]
    edges: list[KnowledgeEdgeSchema]
    analysis_summary: str


class KnowledgeGraphResponse(BaseModel):
    id: UUID
    course_id: Optional[str]
    title: str
    nodes: list[KnowledgeNodeSchema]
    edges: list[KnowledgeEdgeSchema]
    version: int

    class Config:
        from_attributes = True


class NodeResourcesResponse(BaseModel):
    node_id: str
    resources: list[dict]
