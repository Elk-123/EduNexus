"""
Agent模块类型定义
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"

class AgentType(str, Enum):
    MANAGER = "manager"
    PROFESSOR = "professor"
    ARCHITECT = "architect"
    EXAMINER = "examiner"
    DIRECTOR = "director"
    HACKER = "hacker"
    REVIEWER = "reviewer"

@dataclass
class AgentConfig:
    """Agent配置"""
    id: str
    name: str
    role: str
    capabilities: List[str]
    timeout: int = 30000  # 毫秒

@dataclass
class AgentContext:
    """Agent执行上下文"""
    task_id: str
    topic: str
    context: Optional[Dict[str, Any]] = None
    user_input: Optional[str] = None

@dataclass
class AgentResult:
    """Agent执行结果"""
    content: Any
    type: str
    timestamp: datetime
    quality_score: Optional[float] = None
    log: Optional[List[str]] = None

@dataclass
class AgentExecutionResult:
    """Agent执行结果"""
    agent_id: str
    status: AgentStatus
    result: Optional[AgentResult] = None
    error: Optional[str] = None
    duration: int = 0  # 毫秒

@dataclass
class AgentStatusInfo:
    """Agent状态信息"""
    agent_id: str
    status: AgentStatus
    last_updated: datetime
    current_task: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0