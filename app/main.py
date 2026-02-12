from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import auth, projects, test_cases, test_runs

app = FastAPI(title="API Test Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(test_cases.router, prefix="/api/test-cases", tags=["test-cases"])
app.include_router(test_runs.router, prefix="/api/test-runs", tags=["test-runs"])


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    init_db()