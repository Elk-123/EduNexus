import uuid
from sqlalchemy import Column, UUID, JSON, ForeignKey, Integer, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), unique=True, nullable=False)
    
    # 存储 6 维度 JSON: {knowledge_base: 85, cognitive_style: "visual", ...}
    profile_data = Column(JSON, nullable=False)
    
    # 原始对话备份，方便后续微调 LLM
    raw_responses = Column(JSON, nullable=True)
    
    version = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())