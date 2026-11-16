import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, String, Text

from backend.app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class TemplateModel(Base):
    __tablename__ = "templates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(String(20), nullable=False, default="native")
    source_file_id = Column(String(100), nullable=True)
    language = Column(String(10), nullable=False, default="es")
    sections = Column(JSON, nullable=False, default=list)
    style_profile = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
