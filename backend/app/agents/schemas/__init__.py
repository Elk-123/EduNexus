"""
结构化输出 Pydantic 模型 — 替代 try_parse_json() 手动解析

每个 Agent 的输出都由对应的 Pydantic BaseModel 定义。
LangChain 的 with_structured_output() 自动完成：
  JSON Schema 注入 → LLM 输出 → JSON 解析 → Pydantic 校验 → 重试

不再需要手写正则提取 JSON、手动类型检查。
"""

from .manager import ManagerOutput
from .professor import ProfessorOutput
from .architect import ArchitectOutput
from .examiner import ExaminerOutput
from .director import DirectorOutput
from .hacker import HackerOutput
from .reviewer import ReviewerOutput

__all__ = [
    "ManagerOutput",
    "ProfessorOutput",
    "ArchitectOutput",
    "ExaminerOutput",
    "DirectorOutput",
    "HackerOutput",
    "ReviewerOutput",
]
