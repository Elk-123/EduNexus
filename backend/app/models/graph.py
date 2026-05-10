import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class KnowledgeGraph(Base):
    __tablename__ = "knowledge_graphs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    course_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    nodes = Column(JSON, nullable=False)  # [{id, label, type, proficiency, status}, ...]
    edges = Column(JSON, nullable=False)  # [{from, to, isDynamic?}, ...]
    proficiency_data = Column(JSON, default=dict)  # {node_id: proficiency_score}
    analysis_summary = Column(String, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
