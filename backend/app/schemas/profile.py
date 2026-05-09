from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID

# 前端提交的破冰对话数据
class OnboardingSubmission(BaseModel):
    responses: Dict[str, List[str]] = Field(..., example={
        "knowledge_base": ["Python", "Linear Algebra"],
        "cognitive_style": ["Code Practice"],
        "learning_goals": ["Job Hunting"],
        "time_distribution": ["Deep Work"]
    })

# 6 维度画像结构
class ProfileDimensions(BaseModel):
    knowledge_base_score: int      # 知识基础 (0-100)
    cognitive_style: str           # 认知风格
    error_preference: str          # 易错偏好
    learning_goals: str            # 学习目标简述
    focus_duration: int            # 专注时长(min)
    stress_resistance: int         # 抗压值 (0-100)

class ProfileResponse(BaseModel):
    student_id: UUID
    profile_data: ProfileDimensions
    version: int

    class Config:
        from_attributes = True