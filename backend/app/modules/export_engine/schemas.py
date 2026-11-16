from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    document_id: str = Field(..., description="ID del documento a exportar")


class ExportPreviewResponse(BaseModel):
    document_id: str
    filename: str
    unsupported_elements: list[str] = Field(default_factory=list)
