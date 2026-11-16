from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

GenerationStatus = Literal[
    "queued", "processing", "completed", "failed", "accepted", "rejected"
]


class SectionGenerationRequest(BaseModel):
    document_id: str = Field(..., description="ID del documento objetivo")
    section_id: str = Field(..., description="ID o título de la sección")
    section_title: str | None = Field(
        default=None, description="Título visible de la sección"
    )
    user_instructions: str = Field(
        default="", description="Instrucciones específicas del usuario"
    )
    context: dict[str, Any] = Field(
        default_factory=dict, description="Contexto adicional o parámetros"
    )
    source_ids: list[str] = Field(
        default_factory=list, description="Fuentes documentales a considerar"
    )
    expected_document_version: int | None = Field(
        default=None, ge=1, description="Versión esperada del documento"
    )

    model_config = ConfigDict(extra="ignore")


class AcceptGenerationRequest(BaseModel):
    expected_document_version: int | None = Field(
        default=None,
        ge=1,
        description="Versión esperada del documento para prevenir conflictos",
    )


class GenerationResponse(BaseModel):
    generation_id: str
    document_id: str
    section_id: str
    section_title: str
    status: GenerationStatus
    content: dict[str, Any] | None = None
    original_section_content: dict[str, Any] | None = None
    metadata_info: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FullGenerationRequest(BaseModel):
    instructions: str = Field(
        default="", description="Instrucciones globales para todo el documento"
    )
    expected_document_version: int | None = Field(default=None, ge=1)


class FullGenerationResponse(BaseModel):
    document_id: str
    total_sections: int
    generations: list[GenerationResponse]
    status: str
