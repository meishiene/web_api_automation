from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.models.user import Base

class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("api_test_cases.id"), nullable=False)
    status = Column(String(20), nullable=False)  # success, failed, error
    actual_status = Column(Integer)
    actual_body = Column(Text)  # JSON string
    error_message = Column(Text)
    duration_ms = Column(Integer)  # execution duration in milliseconds
    created_at = Column(Integer, nullable=False)