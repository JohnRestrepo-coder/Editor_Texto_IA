from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from backend.app.modules.source_mgmt.extractor import SourceExtractor
from backend.app.modules.source_mgmt.schemas import ExtractedSourceResponse

router = APIRouter(prefix="/sources", tags=["Source Management"])


@router.post(
    "/extract",
    response_model=ExtractedSourceResponse,
    status_code=status.HTTP_200_OK,
    summary="Cargar y extraer texto de un archivo fuente (PDF, DOCX, XLSX, XLS, CSV, TXT)",
)
async def extract_source(
    file: Annotated[UploadFile, File()],
):
    content_bytes = await file.read()
    filename = file.filename or "archivo"

    text, file_type, char_count, success, error = SourceExtractor.extract_text(
        filename=filename, content_bytes=content_bytes
    )

    return ExtractedSourceResponse(
        filename=filename,
        file_type=file_type,
        char_count=char_count,
        extracted_text=text,
        success=success,
        error=error,
    )
