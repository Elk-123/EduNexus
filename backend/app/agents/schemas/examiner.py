"""
Examiner Agent 结构化输出模型
"""
from pydantic import BaseModel, Field


class Question(BaseModel):
    question: str = Field(description="关于指定主题的选择题题干，必须直接涉及主题")
    options: list[str] = Field(description="4个选项，以 A./B./C./D. 开头", min_length=4, max_length=4)
    answer: int = Field(description="正确答案索引 (0=A, 1=B, 2=C, 3=D)", ge=0, le=3)
    explanation: str = Field(description="详细解析，涉及主题知识点")


class ExaminerOutput(BaseModel):
    """考官 Agent 测验输出"""

    questions: list[Question] = Field(description="至少3道选择题", min_length=2)
