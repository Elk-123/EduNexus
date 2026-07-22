"""
Hacker Agent 结构化输出模型
"""
from pydantic import BaseModel, Field


class HackerOutput(BaseModel):
    """极客 Agent 代码输出"""

    title: str = Field(description="代码实验标题，必须包含主题完整关键词")
    description: str = Field(description="说明代码如何演示主题核心概念（50-100字）")
    code: str = Field(description="完整的可运行 Python 代码，含 import/中文注释/主逻辑，至少20行", min_length=50)
    expected_output: str = Field(description="运行代码后的预期输出结果")
    exercises: list[str] = Field(
        description="至少2个练习，每个必须提及主题",
        min_length=2,
        default=[
            "修改代码中的参数，观察行为变化",
            "尝试用另一种方法实现相同功能",
        ],
    )
