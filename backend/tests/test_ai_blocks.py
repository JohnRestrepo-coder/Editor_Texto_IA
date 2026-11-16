import pytest
from fastapi import HTTPException

from backend.app.modules.ai_generation.provider import MockLLMProvider
from backend.app.modules.ai_generation.router import generate_block
from backend.app.modules.ai_generation.schemas import BlockGenerationRequest
from backend.app.modules.document_mgmt.schemas import (
    DocumentContent,
    DocumentCreate,
    Node,
)
from backend.app.modules.document_mgmt.service import DocumentService


def test_generate_block_direct(db_session, monkeypatch):
    monkeypatch.setattr(
        "backend.app.modules.ai_generation.service.get_llm_provider",
        lambda: MockLLMProvider(),
    )

    # 1. Crear documento inicial
    doc = DocumentService.create_document(
        db_session,
        DocumentCreate(
            title="Plan Estratégico",
            content=DocumentContent(
                type="doc",
                content=[
                    Node(
                        type="paragraph",
                        content=[
                            Node(type="text", text="Texto introductorio del usuario.")
                        ],
                    )
                ],
            ),
        ),
    )

    # 2. Solicitar generación para un bloque
    req = BlockGenerationRequest(
        document_id=doc.id,
        block_id="block-test-123",
        section_title="Análisis de Competencia",
        user_instructions="Redacta un análisis breve de competidores basado en las fuentes.",
        mode="analyze",
        sources_text="Competidor A tiene 40% de cuota. Competidor B lidera en precios.",
    )

    res = generate_block(req, db=db_session)
    assert res.block_id == "block-test-123"
    assert res.status == "completed"
    assert res.content is not None
    assert res.content["type"] == "doc"
    assert len(res.content["content"]) > 0


def test_generate_block_not_found_document(db_session):
    req = BlockGenerationRequest(
        document_id="doc-inexistente",
        block_id="block-xyz",
        section_title="Sección Inexistente",
        user_instructions="Cualquier cosa",
    )

    with pytest.raises(HTTPException) as exc_info:
        generate_block(req, db=db_session)
    assert exc_info.value.status_code == 404
