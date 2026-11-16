import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.database import Base
from backend.app.modules.document_mgmt.models import DocumentModel
from backend.app.modules.document_mgmt.schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentContent,
    Node
)
from backend.app.modules.document_mgmt.service import (
    DocumentService,
    DocumentNotFoundError,
    VersionConflictError
)

@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_blank_document(db_session):
    doc_in = DocumentCreate(title="Documento Libre Inicial")
    doc = DocumentService.create_document(db_session, doc_in)

    assert doc.id is not None
    assert doc.title == "Documento Libre Inicial"
    assert doc.version == 1
    assert doc.content["type"] == "doc"
    assert len(doc.content["content"]) == 1

def test_get_document_success(db_session):
    doc = DocumentService.create_document(db_session, DocumentCreate(title="Doc Test"))
    retrieved = DocumentService.get_document(db_session, doc.id)
    assert retrieved.id == doc.id
    assert retrieved.title == "Doc Test"

def test_get_document_not_found(db_session):
    with pytest.raises(DocumentNotFoundError):
        DocumentService.get_document(db_session, "id-inexistente")

def test_update_document_success(db_session):
    doc = DocumentService.create_document(db_session, DocumentCreate(title="Version 1"))

    new_content = DocumentContent(
        type="doc",
        content=[
            Node(
                type="heading",
                attrs={"level": 1},
                content=[Node(type="text", text="Título Principal")]
            )
        ]
    )

    update_in = DocumentUpdate(
        title="Version 2",
        content=new_content,
        expected_version=1
    )

    updated = DocumentService.update_document(db_session, doc.id, update_in)
    assert updated.title == "Version 2"
    assert updated.version == 2
    assert len(updated.content["content"]) == 1
    assert updated.content["content"][0]["type"] == "heading"

def test_update_document_version_conflict(db_session):
    doc = DocumentService.create_document(db_session, DocumentCreate(title="Base"))

    update_in = DocumentUpdate(
        title="Sobrescritura Inválida",
        expected_version=99
    )

    with pytest.raises(VersionConflictError) as exc_info:
        DocumentService.update_document(db_session, doc.id, update_in)

    assert exc_info.value.current_version == 1
    assert exc_info.value.expected_version == 99

def test_schema_rejection_of_unsupported_nodes():
    # Intento de construir contenido con nodo arbitrario
    with pytest.raises(ValidationError):
        Node(type="rawHtmlScript", text="<script></script>")

def test_schema_rejection_of_unsupported_marks():
    with pytest.raises(ValidationError):
        Node(
            type="text",
            text="Texto",
            marks=[{"type": "unsupportedBlinkMark"}]
        )

def test_delete_document(db_session):
    doc = DocumentService.create_document(db_session, DocumentCreate(title="Por borrar"))
    doc_id = doc.id
    DocumentService.delete_document(db_session, doc_id)

    with pytest.raises(DocumentNotFoundError):
        DocumentService.get_document(db_session, doc_id)
