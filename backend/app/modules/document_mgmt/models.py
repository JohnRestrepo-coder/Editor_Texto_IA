import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String

from backend.app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="Documento sin título")
    content = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    template_id = Column(String(64), nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
