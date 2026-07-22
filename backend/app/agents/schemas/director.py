"""
Director Agent 结构化输出模型
"""
from pydantic import BaseModel, Field


class VideoResource(BaseModel):
    type: str = Field(default="video", description="资源类型")
    title: str = Field(description="YouTube 视频标题")
    description: str = Field(description="视频与当前场景主题相关的简介（50-100字）")
    thumbnail: str = Field(description="缩略图 URL，格式 https://img.youtube.com/vi/<视频ID>/maxresdefault.jpg")
    url: str = Field(description="YouTube watch 链接 https://www.youtube.com/watch?v=<视频ID>")
    duration: str = Field(description="视频时长 MM:SS")
    platform: str = Field(default="YouTube", description="平台")


class Scene(BaseModel):
    scene_number: int = Field(description="场景序号")
    title: str = Field(description="与主题直接相关的场景标题")
    visual: str = Field(description="画面描述，与主题直接相关")
    voiceover: str = Field(description="旁白内容（100-200字，口语化，必须围绕主题）")
    duration_seconds: int = Field(default=45, description="场景时长（秒）")
    resources: list[VideoResource] = Field(description="至少1个真实 YouTube 视频资源", min_length=1)


class DirectorOutput(BaseModel):
    """导演 Agent 视频脚本输出"""

    scenes: list[Scene] = Field(description="至少3个场景，从入门到深入", min_length=2)
