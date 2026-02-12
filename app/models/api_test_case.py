from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.models.user import Base

class ApiTestCase(Base):
    __tablename__ = "api_test_cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    url = Column(String(500), nullable=False)
    headers = Column(Text)  # JSON string
    body = Column(Text)      # JSON string
    expected_status = Column(Integer, default=200)
    expected_body = Column(Text)  # JSON string, optional
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)