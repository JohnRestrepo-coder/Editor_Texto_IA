from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.database import get_db_session
from backend.app.modules.document_mgmt.schemas import DocumentResponse
from backend.app.modules.template_mgmt.schemas import (
    DocxInspectionResult,
    TemplateCreate,
    TemplateListItem,
    TemplateResponse,
    TemplateUpdate,
)
from backend.app.modules.template_mgmt.service import (
    InvalidDocxFileError,
    TemplateNotFoundError,
    TemplateService,
)

router = APIRouter(prefix="/templates", tags=["Templates"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una plantilla nativa",
)
def create_template(tpl_in: TemplateCreate, db: DbSession):
    """Crea una plantilla estructurada con secciones e instrucciones."""
    return TemplateService.create_template(db, tpl_in)


@router.get("", response_model=list[TemplateListItem], summary="Listar plantillas")
def list_templates(
    db: DbSession,
    limit: int = 50,
    offset: int = 0,
):
    """Lista las plantillas disponibles ordenadas por actualización."""
    return TemplateService.list_templates(db, limit=limit, offset=offset)


@router.get(
    "/{template_id}", response_model=TemplateResponse, summary="Obtener una plantilla"
)
def get_template(template_id: str, db: DbSession):
    """Recupera la definición completa de una plantilla y sus secciones."""
    try:
        return TemplateService.get_template(db, template_id)
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla '{template_id}' no encontrada",
        )


@router.put(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Actualizar plantilla y mapeo",
)
def update_template(template_id: str, tpl_in: TemplateUpdate, db: DbSession):
    """Actualiza metadatos y configuración de secciones mapeadas."""
    try:
        return TemplateService.update_template(db, template_id, tpl_in)
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla '{template_id}' no encontrada",
        )


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una plantilla",
)
def delete_template(template_id: str, db: DbSession):
    """Elimina la plantilla y su archivo original si era DOCX."""
    try:
        TemplateService.delete_template(db, template_id)
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla '{template_id}' no encontrada",
        )


@router.post(
    "/import-docx",
    response_model=DocxInspectionResult,
    status_code=status.HTTP_201_CREATED,
    summary="Cargar e inspeccionar archivo DOCX existente",
)
async def import_docx(
    file: UploadFile,
    db: DbSession,
):
    """
    Carga un archivo Word (.docx), preserva el binario original de forma segura
    en storage e inspecciona títulos/párrafos para sugerir secciones iniciales.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo inválido",
        )

    content = await file.read()
    try:
        return TemplateService.import_and_inspect_docx(db, content, file.filename)
    except InvalidDocxFileError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.post(
    "/{template_id}/create-document",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo documento desde plantilla",
)
def create_document_from_template(template_id: str, db: DbSession):
    """
    Instancia un nuevo documento en el editor unificado con las secciones,
    encabezados y guías de redacción de la plantilla seleccionada.
    """
    try:
        return TemplateService.create_document_from_template(db, template_id)
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla '{template_id}' no encontrada",
        )
