import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    topic = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending | running | completed | failed
    agents_status = Column(JSON, default=dict)   # {"manager": "running", "professor": "success", ...}
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class GeneratedResource(Base):
    __tablename__ = "generated_resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    task_id = Column(UUID(as_uuid=True), ForeignKey("generation_tasks.id"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    agent_type = Column(String, nullable=False)   # professor | architect | examiner | director | hacker | reviewer
    resource_type = Column(String, nullable=False)  # document | mindmap | quiz | video_script | code_lab | review_report
    content = Column(JSON, nullable=False)
    status = Column(String, default="pending")  # pending | generating | completed | failed
    created_at = Column(DateTime, server_default=func.now())
