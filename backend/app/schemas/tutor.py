from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    message_id: str
    agent_type: str
    timestamp: str


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