from sqlalchemy import CheckConstraint, Column, Index, Integer, String, Text, UniqueConstraint

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class AuditLogArchive(Base):
    __tablename__ = "audit_logs_archive"
    __table_args__ = (
        UniqueConstraint("original_id", name="uq_audit_logs_archive_original_id"),
        CheckConstraint("result IN ('success', 'failed')", name="ck_audit_logs_archive_result_allowed"),
        CheckConstraint("created_at >= 0", name="ck_audit_logs_archive_created_at_non_negative"),
        CheckConstraint("archived_at >= 0", name="ck_audit_logs_archive_archived_at_non_negative"),
        Index("ix_audit_logs_archive_action_created_at", "action", "created_at"),
        Index("ix_audit_logs_archive_user_created_at", "user_id", "created_at"),
        Index("ix_audit_logs_archive_archived_at", "archived_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    original_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    result = Column(String(20), nullable=False, default="success")
    request_id = Column(String(100), nullable=True, index=True)
    client_ip = Column(String(64), nullable=True)
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False)
    archived_at = Column(Integer, nullable=False, default=unix_timestamp)
