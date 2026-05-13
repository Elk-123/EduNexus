from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class WeeklyReport(BaseModel):
    study_hours: float
    completed_courses: int
    average_score: int
    knowledge_mastery: float
    week_start: str
    week_end: str


class StatsData(BaseModel):
    subjects: List[str]
    scores: List[int]
    trend: List[tuple]


class HistoryRecord(BaseModel):
    id: str
    title: str
    type: str
    completed_at: str
    score: int
    duration: str