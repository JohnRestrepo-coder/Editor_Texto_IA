import io
import os

import pytest
from docx import Document as DocxReader
from docx import Document as DocxWriter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.config import settings
from backend.app.database import Base
from backend.app.modules.document_mgmt.schemas import (
    DocumentContent,
    DocumentCreate,
    Node,
)
from backend.app.modules.document_mgmt.service import DocumentService
from backend.app.modules.export_engine.service import ExportService
from backend.app.modules.template_mgmt.schemas import SectionSchema, TemplateCreate
from backend.app.modules.template_mgmt.service import TemplateService


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


def test_export_native_docx(db_session):
    # Crear documento completo con variedad de nodos
    doc_in = DocumentCreate(
        title="Informe Técnico de Prueba",
        content=DocumentContent(
            type="doc",
            content=[
                Node(
                    type="heading",
                    attrs={"level": 1},
                    content=[Node(type="text", text="Capítulo 1: Introducción")],
                ),
                Node(
                    type="paragraph",
                    content=[
                        Node(type="text", text="Texto normal con "),
                        Node(type="text", text="negrita", marks=[{"type": "bold"}]),
                        Node(type="text", text=" y "),
                        Node(type="text", text="cursiva", marks=[{"type": "italic"}]),
                    ],
                ),
                Node(
                    type="bulletList",
                    content=[
                        Node(
                            type="listItem",
                            content=[
                                Node(
                                    type="paragraph",
                                    content=[
                                        Node(type="text", text="Elemento viñeta 1")
                                    ],
                                )
                            ],
                        )
                    ],
                ),
                Node(
                    type="blockquote",
                    content=[Node(type="text", text="Cita textual de referencia.")],
                ),
                Node(
                    type="table",
                    content=[
                        Node(
                            type="tableRow",
                            content=[
                                Node(
                                    type="tableHeader",
                                    content=[
                                        Node(
                                            type="paragraph",
                                            content=[Node(type="text", text="Col A")],
                                        )
                                    ],
                                ),
                                Node(
                                    type="tableHeader",
                                    content=[
                                        Node(
                                            type="paragraph",
                                            content=[Node(type="text", text="Col B")],
                                        )
                                    ],
                                ),
                            ],
                        ),
                        Node(
                            type="tableRow",
                            content=[
                                Node(
                                    type="tableCell",
                                    content=[
                                        Node(
                                            type="paragraph",
                                            content=[Node(type="text", text="Val 1")],
                                        )
                                    ],
                                ),
                                Node(
                                    type="tableCell",
                                    content=[
                                        Node(
                                            type="paragraph",
                                            content=[Node(type="text", text="Val 2")],
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )
    doc = DocumentService.create_document(db_session, doc_in)

    # Exportar a DOCX
    docx_bytes, filename, _warnings = ExportService.export_docx(db_session, doc.id)

    # Validar integridad del archivo
    assert filename == "Informe_Técnico_de_Prueba.docx"
    assert docx_bytes.startswith(b"PK\x03\x04")  # Firma de archivo ZIP/DOCX
    assert len(docx_bytes) > 1000

    # Leer el DOCX generado con python-docx para verificar nodos
    reader = DocxReader(io.BytesIO(docx_bytes))
    paragraphs_text = [p.text for p in reader.paragraphs]
    assert any("Informe Técnico de Prueba" in p for p in paragraphs_text)
    assert any("Capítulo 1: Introducción" in p for p in paragraphs_text)
    assert any("Elemento viñeta 1" in p for p in paragraphs_text)
    assert any("Cita textual de referencia." in p for p in paragraphs_text)

    # Verificar que la tabla se haya creado con sus celdas
    assert len(reader.tables) == 1
    assert reader.tables[0].cell(0, 0).text.strip() == "Col A"
    assert reader.tables[0].cell(1, 1).text.strip() == "Val 2"


def test_export_template_docx_with_preserved_base(db_session):
    # 1. Crear un archivo DOCX patrón de prueba en storage/templates
    base_docx = DocxWriter()
    base_docx.add_heading("Plantilla Corporativa Oficial", level=1)
    base_docx.add_paragraph("Encabezado institucional inmutable.")
    base_file_id = "test-export-template-uuid"
    base_path = os.path.join(settings.STORAGE_DIR, "templates", f"{base_file_id}.docx")
    base_docx.save(base_path)

    try:
        # 2. Registrar plantilla importada
        tpl = TemplateService.create_template(
            db_session,
            TemplateCreate(
                name="Plantilla Corporativa",
                source_type="docx",
                source_file_id=base_file_id,
                sections=[SectionSchema(id="sec_1", title="Alcance", position=0)],
            ),
        )

        # 3. Crear documento enlazado a la plantilla
        doc = DocumentService.create_document(
            db_session,
            DocumentCreate(
                title="Documento con Plantilla",
                template_id=tpl.id,
                content=DocumentContent(
                    type="doc",
                    content=[
                        Node(
                            type="heading",
                            attrs={"level": 2},
                            content=[Node(type="text", text="Alcance del Proyecto")],
                        ),
                        Node(
                            type="paragraph",
                            content=[
                                Node(
                                    type="text",
                                    text="Contenido agregado por el usuario.",
                                )
                            ],
                        ),
                    ],
                ),
            ),
        )

        # 4. Exportar DOCX
        docx_bytes, _filename, _ = ExportService.export_docx(db_session, doc.id)

        # 5. Comprobar que contiene tanto el encabezado original como el contenido nuevo
        reader = DocxReader(io.BytesIO(docx_bytes))
        all_text = " ".join([p.text for p in reader.paragraphs])
        assert "Plantilla Corporativa Oficial" in all_text
        assert "Encabezado institucional inmutable." in all_text
        assert "Alcance del Proyecto" in all_text
        assert "Contenido agregado por el usuario." in all_text

    finally:
        if os.path.exists(base_path):
            os.remove(base_path)


def test_export_pdf_via_playwright(db_session):
    doc_in = DocumentCreate(
        title="Documento para PDF",
        content=DocumentContent(
            type="doc",
            content=[
                Node(
                    type="heading",
                    attrs={"level": 1},
                    content=[Node(type="text", text="Reporte Ejecutivo")],
                ),
                Node(
                    type="paragraph",
                    content=[
                        Node(
                            type="text",
                            text="Este documento se renderiza fielmente a PDF.",
                        )
                    ],
                ),
            ],
        ),
    )
    doc = DocumentService.create_document(db_session, doc_in)

    pdf_bytes, filename, _warnings = ExportService.export_pdf(db_session, doc.id)

    # Validar formato PDF
    assert filename == "Documento_para_PDF.pdf"
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 2000


def test_unsupported_elements_warning_report(db_session):
    from backend.app.modules.document_mgmt.models import DocumentModel

    # Documento en base de datos con contenido JSON que incluye nodo y marca no soportados en DOCX
    doc = DocumentModel(
        id="doc-exotic-test-123",
        title="Documento con Nodos Exóticos",
        content={
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Texto con marca strike no soportada en exportador básico",
                            "marks": [{"type": "strike"}],
                        }
                    ],
                },
                {"type": "unsupported_embed_canvas", "attrs": {"src": "invalid"}},
            ],
        },
    )
    db_session.add(doc)
    db_session.commit()

    _, _, warnings = ExportService.export_docx(db_session, doc.id)

    # Se debe emitir advertencia explícita y no ignorarse en silencio
    assert len(warnings) >= 1
    assert any("unsupported_embed_canvas" in w or "strike" in w for w in warnings)


def test_html_preview_render(db_session):
    doc_in = DocumentCreate(
        title="Vista Previa Documento",
        content=DocumentContent(
            type="doc",
            content=[
                Node(
                    type="heading",
                    attrs={"level": 2},
                    content=[Node(type="text", text="Sección Vista Previa")],
                ),
                Node(
                    type="paragraph",
                    content=[
                        Node(type="text", text="Texto con "),
                        Node(type="text", text="negrita", marks=[{"type": "bold"}]),
                    ],
                ),
            ],
        ),
    )
    doc = DocumentService.create_document(db_session, doc_in)

    html_result = ExportService.render_html_preview(db_session, doc.id)

    assert "<!DOCTYPE html>" in html_result
    assert "Vista Previa Documento" in html_result
    assert "<h2>Sección Vista Previa</h2>" in html_result
    assert "<strong>negrita</strong>" in html_result


def test_export_docx_with_override_content_and_ai_block(db_session):
    # Crear documento inicialmente vacío en base de datos
    doc = DocumentService.create_document(
        db_session,
        DocumentCreate(title="Documento Inicial Vacio"),
    )

    # Simular contenido editado en el frontend con párrafos y un bloque de IA
    in_memory_content = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "Párrafo 1 escrito por el usuario en el editor.",
                    }
                ],
            },
            {
                "type": "aiBlock",
                "attrs": {
                    "id": "block-1",
                    "sectionTitle": "Análisis Financiero",
                    "instructions": "Proyección Q3",
                },
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Párrafo posterior al bloque de IA."}
                ],
            },
        ],
    }

    docx_bytes, _filename, _warnings = ExportService.export_docx(
        db_session,
        doc.id,
        override_title="Documento_Con_Contenido_Real",
        override_content=in_memory_content,
    )

    reader = DocxReader(io.BytesIO(docx_bytes))
    all_text = " ".join([p.text for p in reader.paragraphs])

    assert "Documento_Con_Contenido_Real" in all_text
    assert "Párrafo 1 escrito por el usuario en el editor." in all_text
    assert "Análisis Financiero" in all_text
    assert "Párrafo posterior al bloque de IA." in all_text
