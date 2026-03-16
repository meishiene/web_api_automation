from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.lifecycle import unix_timestamp
from app.models.user import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_projects_owner_id_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_projects_name_not_blank"),
        CheckConstraint("created_at >= 0", name="ck_projects_created_at_non_negative"),
        Index("ix_projects_owner_id", "owner_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    owner = relationship("User", back_populates="projects")
    organization = relationship("Organization", back_populates="projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    test_cases = relationship("ApiTestCase", back_populates="project", cascade="all, delete-orphan")
    test_suites = relationship("ApiTestSuite", back_populates="project", cascade="all, delete-orphan")
    environments = relationship("ProjectEnvironment", back_populates="project", cascade="all, delete-orphan")
    project_variables = relationship("ProjectVariable", back_populates="project", cascade="all, delete-orphan")
    batch_runs = relationship("ApiBatchRun", back_populates="project", cascade="all, delete-orphan")
    schedule_tasks = relationship("ScheduleTask", back_populates="project", cascade="all, delete-orphan")
    run_queue_items = relationship("RunQueue", back_populates="project", cascade="all, delete-orphan")
    web_test_cases = relationship("WebTestCase", back_populates="project", cascade="all, delete-orphan")
    web_locators = relationship("WebLocator", back_populates="project", cascade="all, delete-orphan")
    web_test_runs = relationship("WebTestRun", back_populates="project", cascade="all, delete-orphan")
