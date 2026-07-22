"""
Professor Agent 结构化输出模型
"""
from pydantic import BaseModel, Field


class SubSection(BaseModel):
    subheading: str = Field(description="小节标题")
    body: str = Field(description="小节详细内容，至少150字，与主题直接相关", min_length=50)


class Section(BaseModel):
    heading: str = Field(description="章节标题，必须直接提及用户指定的主题")
    subsections: list[SubSection] = Field(description="至少2个小节", min_length=1)


class ProfessorOutput(BaseModel):
    """教授 Agent 教学内容输出"""

    title: str = Field(description="课程标题，必须包含用户指定的主题关键词")
    sections: list[Section] = Field(description="至少3个章节", min_length=2)
