from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class DefectSyncRecord(Base):
    __tablename__ = "defect_sync_records"
    __table_args__ = (
        UniqueConstraint("project_id", "failure_fingerprint", name="uq_defect_sync_project_fingerprint"),
        CheckConstraint("length(trim(run_type)) > 0", name="ck_defect_sync_run_type_not_blank"),
        CheckConstraint("run_type IN ('api', 'web')", name="ck_defect_sync_run_type_allowed"),
        CheckConstraint("length(trim(issue_key)) > 0", name="ck_defect_sync_issue_key_not_blank"),
        CheckConstraint("occurrence_count >= 1", name="ck_defect_sync_occurrence_positive"),
        CheckConstraint("created_at >= 0", name="ck_defect_sync_created_at_non_negative"),
        CheckConstraint("updated_at >= 0", name="ck_defect_sync_updated_at_non_negative"),
        Index("ix_defect_sync_project_id", "project_id"),
        Index("ix_defect_sync_config_id", "integration_config_id"),
        Index("ix_defect_sync_issue_key", "issue_key"),
    )

    id = Column(Integer, primary_key=True, index=True)
    integration_config_id = Column(Integer, ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    run_type = Column(String(20), nullable=False)
    last_run_id = Column(Integer, nullable=False)
    case_id = Column(Integer, nullable=True)
    case_name = Column(String(255), nullable=False)
    failure_fingerprint = Column(String(128), nullable=False)
    failure_category = Column(String(100), nullable=True)
    failure_message = Column(Text, nullable=True)
    issue_key = Column(String(100), nullable=False)
    issue_url = Column(String(500), nullable=True)
    issue_status = Column(String(50), nullable=False, default="open")
    summary = Column(String(255), nullable=False)
    detail_api_path = Column(String(500), nullable=True)
    tags_json = Column(Text, nullable=True)
    last_payload_json = Column(Text, nullable=True)
    occurrence_count = Column(Integer, nullable=False, default=1)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)
    updated_at = Column(Integer, nullable=False, default=unix_timestamp, onupdate=unix_timestamp)

    project = relationship("Project", back_populates="defect_sync_records")
    integration_config = relationship("IntegrationConfig", back_populates="defect_sync_records")
