from app.config import Settings


def test_resolved_database_url_defaults_to_sqlite_local():
    settings = Settings()
    assert settings.resolved_database_url == "sqlite:///./test_platform.db"


def test_resolved_database_url_uses_postgres_for_local_when_enabled():
    settings = Settings(
        USE_POSTGRES=True,
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="postgres",
        POSTGRES_DB="dev_db",
    )
    assert settings.resolved_database_url == "postgresql+psycopg://postgres:postgres@localhost:5432/dev_db"


def test_resolved_database_url_prefers_test_database_url():
    settings = Settings(
        APP_ENV="test",
        TEST_DATABASE_URL="postgresql+psycopg://tester:pwd@localhost:5432/test_db",
    )
    assert settings.resolved_database_url == "postgresql+psycopg://tester:pwd@localhost:5432/test_db"


def test_resolved_database_url_uses_postgres_test_db_when_enabled():
    settings = Settings(
        APP_ENV="test",
        USE_POSTGRES=True,
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="postgres",
        POSTGRES_TEST_DB="test_db",
    )
    assert settings.resolved_database_url == "postgresql+psycopg://postgres:postgres@localhost:5432/test_db"

