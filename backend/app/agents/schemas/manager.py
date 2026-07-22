"""
Manager Agent 结构化输出模型
"""
from pydantic import BaseModel, Field


class ManagerOutput(BaseModel):
    """Manager Agent 任务计划输出 — 自动校验 JSON 结构"""

    tasks: list[str] = Field(
        description="恰好7个任务，每个任务必须明确提及用户指定的主题",
        min_length=5,
        max_length=10,
    )
    priority: list[str] = Field(
        description="Agent 执行优先级顺序",
        default=["professor", "architect", "examiner", "director", "hacker", "reviewer"],
    )
    coordination_notes: list[str] = Field(
        description="协调说明，描述各 Agent 之间的依赖关系",
        default=[],
    )
