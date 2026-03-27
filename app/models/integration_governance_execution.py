from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class IntegrationGovernanceExecution(Base):
    __tablename__ = "integration_governance_executions"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "execution_type",
            "idempotency_key",
            name="uq_integration_governance_executions_project_type_key",
        ),
        CheckConstraint(
            "execution_type IN ('retry_failed')",
            name="ck_integration_governance_executions_type_allowed",
        ),
        CheckConstraint(
            "status IN ('completed', 'failed')",
            name="ck_integration_governance_executions_status_allowed",
        ),
        CheckConstraint("length(trim(idempotency_key)) > 0", name="ck_integration_governance_executions_key_not_blank"),
        CheckConstraint("created_at >= 0", name="ck_integration_governance_executions_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_integration_governance_executions_updated_at_non_negative"),
        CheckConstraint("completed_at >= 0", name="ck_integration_governance_executions_completed_at_non_negative"),
        Index(
            "ix_integration_governance_executions_project_type_created",
            "project_id",
            "execution_type",
            "created_at",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    execution_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="completed")
    idempotency_key = Column(String(128), nullable=False)
    request_json = Column(Text, nullable=False)
    result_json = Column(Text, nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    completed_at = Column(Integer, nullable=False)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="integration_governance_executions")
