from sqlalchemy import CheckConstraint, Column, Index, Integer, String, Text

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint("result IN ('success', 'failed')", name="ck_audit_logs_result_allowed"),
        CheckConstraint("created_at >= 0", name="ck_audit_logs_created_at_non_negative"),
        Index("ix_audit_logs_action_created_at", "action", "created_at"),
        Index("ix_audit_logs_user_created_at", "user_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
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
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
