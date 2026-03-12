from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class ScheduleTask(Base):
    __tablename__ = "schedule_tasks"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_schedule_tasks_project_id_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_schedule_tasks_name_not_blank"),
        CheckConstraint("length(trim(cron_expr)) > 0", name="ck_schedule_tasks_cron_expr_not_blank"),
        CheckConstraint("enabled IN (0, 1)", name="ck_schedule_tasks_enabled_flag"),
        CheckConstraint(
            "target_type IN ('test_case', 'test_suite', 'tag', 'custom')",
            name="ck_schedule_tasks_target_type_allowed",
        ),
        CheckConstraint("created_at >= 0", name="ck_schedule_tasks_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_schedule_tasks_updated_at_non_negative"),
        Index("ix_schedule_tasks_project_enabled", "project_id", "enabled"),
        Index("ix_schedule_tasks_created_by_updated_at", "created_by", "updated_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    cron_expr = Column(String(100), nullable=False)
    timezone = Column(String(50), nullable=False, default="UTC")
    enabled = Column(Integer, nullable=False, default=1)

    # target_type: test_case | test_suite | tag | custom
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=True, index=True)

    # payload: JSON string for run parameters (env, dataset, concurrency, etc.)
    payload = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="schedule_tasks")
    creator = relationship("User", back_populates="schedule_tasks")
