from sqlalchemy import CheckConstraint, Column, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from app.models.lifecycle import unix_timestamp

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(trim(username)) > 0", name="ck_users_username_not_blank"),
        CheckConstraint("role IN ('admin', 'user')", name="ck_users_role_allowed"),
        CheckConstraint("created_at >= 0", name="ck_users_created_at_non_negative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    role = Column(String(20), nullable=False, default="user")
    password = Column(String(255), nullable=False)
    created_at = Column(Integer, nullable=False, default=unix_timestamp)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    organizations_owned = relationship("Organization", back_populates="owner", cascade="all, delete-orphan")
    organization_memberships = relationship("OrganizationMember", back_populates="user", cascade="all, delete-orphan")
    created_test_suites = relationship("ApiTestSuite", back_populates="creator", cascade="all, delete-orphan")
    created_environments = relationship("ProjectEnvironment", back_populates="creator", cascade="all, delete-orphan")
    triggered_batch_runs = relationship("ApiBatchRun", back_populates="trigger_user")
    schedule_tasks = relationship("ScheduleTask", back_populates="creator", cascade="all, delete-orphan")
    execution_tasks_created = relationship("ExecutionTask", back_populates="creator")
    identity_provider_bindings = relationship(
        "IdentityProviderBinding",
        back_populates="user",
        cascade="all, delete-orphan",
    )
