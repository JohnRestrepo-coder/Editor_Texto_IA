from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SourceType = Literal["native", "docx"]


class SectionSchema(BaseModel):
    id: str = Field(..., min_length=1, description="Identificador único de la sección")
    title: str = Field(..., min_length=1, description="Título visible de la sección")
    position: int = Field(
        default=0, ge=0, description="Posición u orden en el documento"
    )
    required: bool = Field(default=True, description="Si la sección es obligatoria")
    instructions: str = Field(
        default="", description="Instrucciones para redacción o generación IA"
    )
    generation_enabled: bool = Field(
        default=True, description="Si permite generación automática"
    )
    depends_on: list[str] = Field(
        default_factory=list, description="IDs de secciones previas de las que depende"
    )

    model_config = ConfigDict(extra="forbid")


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    source_type: SourceType = "native"
    source_file_id: str | None = None
    language: str = Field(default="es")
    sections: list[SectionSchema] = Field(default_factory=list)
    style_profile: dict[str, Any] | None = None


class TemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    language: str | None = None
    sections: list[SectionSchema] | None = None
    style_profile: dict[str, Any] | None = None


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    source_type: SourceType
    source_file_id: str | None = None
    language: str
    sections: list[SectionSchema]
    style_profile: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TemplateListItem(BaseModel):
    id: str
    name: str
    description: str | None = None
    source_type: SourceType
    sections_count: int
    created_at: datetime
    updated_at: datetime


class DocxInspectionResult(BaseModel):
    template_id: str
    filename: str
    source_file_id: str
    detected_sections: list[SectionSchema]
    headings_count: int
    paragraphs_count: int
    tables_count: int
    unsupported_elements: list[str] = Field(default_factory=list)
