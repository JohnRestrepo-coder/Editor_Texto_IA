from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database import get_db_session
from backend.app.modules.ai_generation.schemas import (
    AcceptGenerationRequest,
    FullGenerationRequest,
    FullGenerationResponse,
    GenerationResponse,
    SectionGenerationRequest,
)
from backend.app.modules.ai_generation.service import AIGenerationService
from backend.app.modules.document_mgmt.schemas import DocumentResponse

router = APIRouter(prefix="/generations", tags=["AI Generation"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/section",
    response_model=GenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar propuesta para una sección",
)
def generate_section(
    req: SectionGenerationRequest,
    db: DbSession,
):
    return AIGenerationService.generate_section(db, req)


@router.get(
    "/{generation_id}",
    response_model=GenerationResponse,
    summary="Obtener detalle de una propuesta",
)
def get_generation(
    generation_id: str,
    db: DbSession,
):
    return AIGenerationService.get_generation(db, generation_id)


@router.post(
    "/{generation_id}/accept",
    response_model=DocumentResponse,
    summary="Aceptar y aplicar propuesta al documento",
)
def accept_generation(
    generation_id: str,
    db: DbSession,
    req: AcceptGenerationRequest | None = None,
):
    expected_ver = req.expected_document_version if req else None
    return AIGenerationService.accept_generation(
        db, generation_id, expected_version=expected_ver
    )


@router.post(
    "/{generation_id}/reject",
    response_model=GenerationResponse,
    summary="Rechazar propuesta sin alterar documento",
)
def reject_generation(
    generation_id: str,
    db: DbSession,
):
    return AIGenerationService.reject_generation(db, generation_id)


@router.post(
    "/document/{document_id}/generate-all",
    response_model=FullGenerationResponse,
    summary="Orquestar generación de documento completo",
)
def generate_all(
    document_id: str,
    req: FullGenerationRequest,
    db: DbSession,
):
    return AIGenerationService.orchestrate_full_generation(db, document_id, req)


@router.get(
    "/document/{document_id}",
    response_model=list[GenerationResponse],
    summary="Listar historial de propuestas del documento",
)
def list_document_generations(
    document_id: str,
    db: DbSession,
):
    return AIGenerationService.list_document_generations(db, document_id)
