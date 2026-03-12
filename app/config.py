from typing import Literal, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: Literal["local", "test", "prod"] = "local"
    USE_POSTGRES: bool = False

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    PASSWORD_HASH_ITERATIONS: int = 120000

    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: Optional[str] = None

    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "web_api_automation_dev"
    POSTGRES_TEST_DB: str = "web_api_automation_test"
    AUDIT_LOG_ACTIVE_RETENTION_DAYS: int = 30
    AUDIT_LOG_ARCHIVE_RETENTION_DAYS: int = 180
    AUDIT_LOG_RETENTION_BATCH_SIZE: int = 500
    AUDIT_GOVERNANCE_LOCK_FILE: str = "./artifacts/audit-governance/audit-governance.lock"
    AUDIT_GOVERNANCE_MANIFEST_DIR: str = "./artifacts/audit-governance"
    AUDIT_GOVERNANCE_ALERT_OUTPUT: Optional[str] = None
    AUDIT_GOVERNANCE_FAIL_ON_ALERT: bool = False
    AUDIT_GOVERNANCE_MAX_CANDIDATE_ARCHIVE_COUNT: Optional[int] = None
    AUDIT_GOVERNANCE_MAX_CANDIDATE_DELETE_ARCHIVE_COUNT: Optional[int] = None
    AUDIT_GOVERNANCE_MAX_ARCHIVED_COUNT: Optional[int] = None
    AUDIT_GOVERNANCE_MAX_DELETED_ARCHIVE_COUNT: Optional[int] = None

    def _postgres_url(self, db_name: str) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{db_name}"
        )

    @property
    def resolved_database_url(self) -> str:
        if self.APP_ENV == "test" and self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL

        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.APP_ENV == "test":
            if self.USE_POSTGRES:
                return self._postgres_url(self.POSTGRES_TEST_DB)
            return "sqlite:///./test_platform_test.db"

        if self.USE_POSTGRES:
            return self._postgres_url(self.POSTGRES_DB)
        return "sqlite:///./test_platform.db"


settings = Settings()
