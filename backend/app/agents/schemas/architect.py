"""
Architect Agent 结构化输出模型
"""
from pydantic import BaseModel, Field


class MindMapNode(BaseModel):
    name: str = Field(description="节点名称，简洁明了（10字以内）")
    children: list["MindMapNode"] = Field(description="子节点列表", default=[])


class MindMap(BaseModel):
    root: str = Field(description="根节点，必须包含主题关键词")
    children: list[MindMapNode] = Field(description="至少3个一级分支", min_length=2)


class ArchitectOutput(BaseModel):
    """架构师 Agent 思维导图输出"""

    mindmap: MindMap = Field(description="思维导图结构")
