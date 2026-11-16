from typing import Any

from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    document_id: str = Field(..., description="ID del documento a exportar")
    title: str | None = Field(default=None, description="Título opcional para exportar")
    content: dict[str, Any] | None = Field(
        default=None,
        description="Contenido estructurado opcional del editor a exportar",
    )


class ExportPreviewResponse(BaseModel):
    document_id: str
    filename: str
    unsupported_elements: list[str] = Field(default_factory=list)
