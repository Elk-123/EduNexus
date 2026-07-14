from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


# ── 文本聊天 ──

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    message_id: str
    agent_type: str
    timestamp: str


# ── AI 搜题（图片解题）──

class SolveRequest(BaseModel):
    """图片解题请求"""
    image_base64: str = Field(..., description="题目的 base64 编码图片")
    message: Optional[str] = Field(default="请帮我解答这道题目", description="附加的文字说明")


class SolveStep(BaseModel):
    """解题步骤"""
    title: str = Field(..., description="步骤标题，如 'Step 1：分析题目'")
    content: List[str] = Field(..., description="步骤内容，每个元素是一行文本")


class SolveResponse(BaseModel):
    """图片解题响应"""
    steps: List[SolveStep] = Field(..., description="解题步骤列表")
    summary: str = Field(..., description="最终结论总结")
    raw_text: Optional[str] = Field(default=None, description="原始题目文本（OCR/识别结果）")


# ── 对话历史 ──

class Message(BaseModel):
    id: str
    content: str
    role: str  # "user" or "ai"
    timestamp: str
    agent_type: Optional[str] = None


class ConversationHistory(BaseModel):
    id: str
    topic: str
    preview: str
    timestamp: str
    message_count: int
