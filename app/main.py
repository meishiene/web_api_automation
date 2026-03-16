import logging
import time
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    audit_logs,
    auth,
    environments,
    organizations,
    projects,
    queue_worker,
    schedule_tasks,
    test_cases,
    test_runs,
    test_suites,
    web_test_cases,
    web_test_runs,
)
from app.config import settings
from app.database import auto_migrate_db, init_db
from app.errors import register_exception_handlers
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("app.request")

app = FastAPI(title="API Test Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.middleware("http")
async def request_id_middleware(request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.exception(
            "request_failed",
            extra={
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
            },
        )
        raise

    duration_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_completed",
        extra={
            "event": "http_request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else None,
        },
    )
    return response


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(organizations.router, prefix="/api/organizations", tags=["organizations"])
app.include_router(test_cases.router, prefix="/api/test-cases", tags=["test-cases"])
app.include_router(test_suites.router, prefix="/api/test-suites", tags=["test-suites"])
app.include_router(environments.router, prefix="/api/environments", tags=["environments"])
app.include_router(schedule_tasks.router, prefix="/api/schedule-tasks", tags=["schedule-tasks"])
app.include_router(queue_worker.router, prefix="/api/run-queue", tags=["run-queue"])
app.include_router(test_runs.router, prefix="/api/test-runs", tags=["test-runs"])
app.include_router(audit_logs.router, prefix="/api/audit-logs", tags=["audit-logs"])
app.include_router(web_test_cases.router, prefix="/api/web-test-cases", tags=["web-test-cases"])
app.include_router(web_test_runs.router, prefix="/api/web-test-runs", tags=["web-test-runs"])


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    auto_migrate_db()
    init_db()
