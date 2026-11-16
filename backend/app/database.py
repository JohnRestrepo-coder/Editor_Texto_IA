from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.DATABASE_URL
    else {},
    echo=(settings.ENVIRONMENT == "development"),
)

session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session():
    session: Session = session_factory()
    try:
        yield session
    finally:
        session.close()


def init_db():
    # Import models to ensure they are registered with Base.metadata
    import backend.app.modules.document_mgmt.models
    import backend.app.modules.template_mgmt.models  # noqa

    Base.metadata.create_all(bind=engine)
