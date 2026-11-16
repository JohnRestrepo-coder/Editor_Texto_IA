import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.config import settings
from backend.app.database import Base

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def configure_test_environment(monkeypatch):
    """Garantiza que la suite de pruebas unitarias utilice el proveedor simulado sin costo ni dependencia de red."""
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock")


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
