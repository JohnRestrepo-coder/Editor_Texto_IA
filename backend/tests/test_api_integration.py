import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.modules.document_mgmt.router import (
    create_document,
    delete_document,
    get_document,
    list_documents,
    update_document,
)
from backend.app.modules.document_mgmt.schemas import (
    DocumentContent,
    DocumentCreate,
    DocumentUpdate,
    Node,
)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_api_document_lifecycle(db_session):
    # 1. Crear documento a través del handler del router
    create_payload = DocumentCreate(title="Documento Integración API")
    created = create_document(create_payload, db=db_session)
    assert created.id is not None
    assert created.title == "Documento Integración API"
    assert created.version == 1

    # 2. Listar documentos
    docs_list = list_documents(db=db_session)
    assert len(docs_list) >= 1
    assert any(d.id == created.id for d in docs_list)

    # 3. Obtener por ID
    fetched = get_document(created.id, db=db_session)
    assert fetched.id == created.id

    # 4. Actualizar con versión optimista válida
    update_payload = DocumentUpdate(
        title="Documento Actualizado API",
        expected_version=1,
        content=DocumentContent(
            type="doc",
            content=[
                Node(
                    type="paragraph",
                    content=[Node(type="text", text="Texto enriquecido integrado")],
                )
            ],
        ),
    )
    updated = update_document(created.id, update_payload, db=db_session)
    assert updated.version == 2
    assert updated.title == "Documento Actualizado API"

    # 5. Intentar actualizar con versión obsoleta (debe lanzar 409 Conflict)
    obsolete_payload = DocumentUpdate(
        title="Sobrescritura No Permitida", expected_version=1
    )
    with pytest.raises(HTTPException) as exc_conflict:
        update_document(created.id, obsolete_payload, db=db_session)
    assert exc_conflict.value.status_code == 409

    # 6. Eliminar documento
    delete_document(created.id, db=db_session)

    # 7. Verificar que ya no existe (404 Not Found)
    with pytest.raises(HTTPException) as exc_404:
        get_document(created.id, db=db_session)
    assert exc_404.value.status_code == 404
