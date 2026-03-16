from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class WorkerHeartbeat(Base):
    __tablename__ = "worker_heartbeats"
    __table_args__ = (
        UniqueConstraint("project_id", "worker_id", name="uq_worker_heartbeats_project_worker"),
        CheckConstraint(
            "run_type IS NULL OR run_type IN ('api', 'web')",
            name="ck_worker_heartbeats_run_type_allowed",
        ),
        CheckConstraint(
            "status IN ('online', 'busy', 'offline')",
            name="ck_worker_heartbeats_status_allowed",
        ),
        CheckConstraint(
            "last_heartbeat_at >= 0",
            name="ck_worker_heartbeats_last_heartbeat_at_non_negative",
        ),
        CheckConstraint(
            "created_at >= 0",
            name="ck_worker_heartbeats_created_at_non_negative",
        ),
        CheckConstraint(
            "updated_at >= 0",
            name="ck_worker_heartbeats_updated_at_non_negative",
        ),
        Index(
            "ix_worker_heartbeats_project_status_last_heartbeat",
            "project_id",
            "status",
            "last_heartbeat_at",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    worker_id = Column(String(100), nullable=False, index=True)
    run_type = Column(String(20), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="online")
    current_queue_item_id = Column(Integer, ForeignKey("run_queue.id", ondelete="SET NULL"), nullable=True)
    last_heartbeat_at = Column(Integer, nullable=False, default=unix_timestamp)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp)

    project = relationship("Project", back_populates="worker_heartbeats")
    current_queue_item = relationship("RunQueue")
