from pydantic import BaseModel, Field


class ExtractedSourceResponse(BaseModel):
    filename: str = Field(..., description="Nombre del archivo cargado")
    file_type: str = Field(..., description="Extensión o tipo detectado")
    char_count: int = Field(0, description="Cantidad de caracteres de texto extraído")
    extracted_text: str = Field(
        "", description="Contenido textual extraído del archivo"
    )
    success: bool = Field(True, description="Indica si la extracción fue exitosa")
    error: str | None = Field(
        None, description="Mensaje de error si la extracción falló"
    )
