from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db_session
from backend.app.modules.document_mgmt.schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListItem
)
from backend.app.modules.document_mgmt.service import (
    DocumentService,
    DocumentNotFoundError,
    VersionConflictError
)

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo documento"
)
def create_document(
    doc_in: DocumentCreate,
    db: Session = Depends(get_db_session)
):
    """Crea un documento en blanco o inicializado con contenido/plantilla."""
    doc = DocumentService.create_document(db, doc_in)
    return doc

@router.get(
    "",
    response_model=List[DocumentListItem],
    summary="Listar documentos"
)
def list_documents(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db_session)
):
    """Retorna la lista de documentos registrados ordenados por última actualización."""
    return DocumentService.list_documents(db, limit=limit, offset=offset)

@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Obtener un documento por ID"
)
def get_document(
    document_id: str,
    db: Session = Depends(get_db_session)
):
    """Recupera el contenido completo y metadatos de un documento."""
    try:
        return DocumentService.get_document(db, document_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID '{document_id}' no encontrado."
        )

@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Actualizar documento con control de versión optimista"
)
def update_document(
    document_id: str,
    doc_in: DocumentUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Actualiza el documento. Requiere 'expected_version'.
    Si la versión no coincide con la versión actual en base de datos, retorna 409 Conflict.
    """
    try:
        return DocumentService.update_document(db, document_id, doc_in)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID '{document_id}' no encontrado."
        )
    except VersionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": str(e),
                "current_version": e.current_version,
                "expected_version": e.expected_version
            }
        )

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un documento"
)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db_session)
):
    """Elimina permanentemente el documento."""
    try:
        DocumentService.delete_document(db, document_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID '{document_id}' no encontrado."
        )
