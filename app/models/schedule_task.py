from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.models.user import Base


class ScheduleTask(Base):
    __tablename__ = "schedule_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    cron_expr = Column(String(100), nullable=False)
    timezone = Column(String(50), nullable=False, default="UTC")
    enabled = Column(Integer, nullable=False, default=1)

    # target_type: test_case | test_suite | tag | custom
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=True, index=True)

    # payload: JSON string for run parameters (env, dataset, concurrency, etc.)
    payload = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)
