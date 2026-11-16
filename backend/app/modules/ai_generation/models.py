import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text

from backend.app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class GenerationModel(Base):
    __tablename__ = "generations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), nullable=False, index=True)
    section_id = Column(String(64), nullable=False)
    section_title = Column(String(255), nullable=False, default="")
    status = Column(
        String(32),
        nullable=False,
        default="completed",  # queued, processing, completed, failed, accepted, rejected
    )
    user_instructions = Column(Text, nullable=True, default="")
    content = Column(JSON, nullable=True)  # Contenido Tiptap propuesto
    original_section_content = Column(JSON, nullable=True)  # Snapshot previo
    provider = Column(String(64), nullable=False, default="mock")
    model = Column(String(64), nullable=False, default="mock-v1")
    prompt_version = Column(String(32), nullable=False, default="v1")
    latency_ms = Column(Integer, nullable=False, default=0)
    tokens_used = Column(Integer, nullable=True, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
