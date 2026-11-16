import io
import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session

from backend.app.database import get_db_session
from backend.app.modules.export_engine.schemas import ExportRequest
from backend.app.modules.export_engine.service import ExportService

router = APIRouter(prefix="/exports", tags=["Document Export"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/docx",
    summary="Exportar documento en formato DOCX",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}
            },
            "description": "Archivo binario DOCX generado.",
        }
    },
)
def export_docx(
    db: DbSession,
    body: ExportRequest | None = None,
    document_id: str | None = Query(default=None),
):
    target_id = body.document_id if body else document_id
    if not target_id:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere document_id en el cuerpo o como parámetro de consulta.",
        )

    file_bytes, filename, unsupported = ExportService.export_docx(db, target_id)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Access-Control-Expose-Headers": "X-Unsupported-Elements",
        "X-Unsupported-Elements": json.dumps(unsupported),
    }

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.post(
    "/pdf",
    summary="Exportar documento en formato PDF",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Archivo binario PDF generado.",
        }
    },
)
def export_pdf(
    db: DbSession,
    body: ExportRequest | None = None,
    document_id: str | None = Query(default=None),
):
    target_id = body.document_id if body else document_id
    if not target_id:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere document_id en el cuerpo o como parámetro de consulta.",
        )

    file_bytes, filename, unsupported = ExportService.export_pdf(db, target_id)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Access-Control-Expose-Headers": "X-Unsupported-Elements",
        "X-Unsupported-Elements": json.dumps(unsupported),
    }

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/pdf",
        headers=headers,
    )


@router.get(
    "/{document_id}/preview",
    response_class=HTMLResponse,
    summary="Vista previa HTML de fidelidad de impresión",
)
def preview_html(
    document_id: str,
    db: DbSession,
):
    html_content = ExportService.render_html_preview(db, document_id)
    return HTMLResponse(content=html_content)
