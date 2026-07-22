"""
Reviewer Agent 结构化输出模型
"""
from pydantic import BaseModel, Field
from typing import Literal


class ReviewerOutput(BaseModel):
    """审查员 Agent 质量审查输出"""

    hallucination_risk: Literal["low", "medium", "high"] = Field(
        default="low",
        description="幻觉风险评估",
    )
    quality_score: int = Field(
        description="质量评分 0-100",
        ge=0,
        le=100,
        default=85,
    )
    suggestions: list[str] = Field(
        description="2-4条改进建议，每条必须具体到主题的某个知识点",
        min_length=2,
        max_length=5,
    )
    difficulty_assessment: str = Field(
        description="针对主题学习内容的难度评估，说明适合什么水平的学习者",
    )
