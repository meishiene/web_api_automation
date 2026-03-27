from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models.user import Base

# Ensure all models are imported so SQLAlchemy metadata has every table.
from app.models import api_batch_run  # noqa: F401
from app.models import api_batch_run_item  # noqa: F401
from app.models import api_test_case  # noqa: F401
from app.models import api_test_suite  # noqa: F401
from app.models import api_test_suite_case  # noqa: F401
from app.models import audit_log  # noqa: F401
from app.models import audit_log_archive  # noqa: F401
from app.models import defect_sync_record  # noqa: F401
from app.models import environment_variable  # noqa: F401
from app.models import execution_job  # noqa: F401
from app.models import execution_task  # noqa: F401
from app.models import integration_config  # noqa: F401
from app.models import integration_event  # noqa: F401
from app.models import integration_governance_execution  # noqa: F401
from app.models import identity_oauth_session  # noqa: F401
from app.models import identity_provider_binding  # noqa: F401
from app.models import notification_delivery  # noqa: F401
from app.models import notification_subscription  # noqa: F401
from app.models import organization  # noqa: F401
from app.models import organization_member  # noqa: F401
from app.models import project  # noqa: F401
from app.models import project_environment  # noqa: F401
from app.models import project_member  # noqa: F401
from app.models import project_variable  # noqa: F401
from app.models import run_queue  # noqa: F401
from app.models import schedule_task  # noqa: F401
from app.models import test_run  # noqa: F401
from app.models import web_locator  # noqa: F401
from app.models import web_step  # noqa: F401
from app.models import web_test_case  # noqa: F401
from app.models import web_test_run  # noqa: F401
from app.models import worker_heartbeat  # noqa: F401
from app.models import user  # noqa: F401

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_user_and_login_impl(client: TestClient, username: str, password: str) -> str:
    register_resp = client.post("/api/auth/register", json={"username": username, "password": password})
    assert register_resp.status_code == 200
    login_resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def create_user_and_login(client):
    def _create(username: str, password: str) -> str:
        return create_user_and_login_impl(client, username, password)

    return _create


@pytest.fixture()
def auth_headers():
    def _headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    return _headers


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


