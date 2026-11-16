import io

import pytest
from docx import Document as DocxWriter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.modules.template_mgmt.schemas import (
    SectionSchema,
    TemplateCreate,
    TemplateUpdate,
)
from backend.app.modules.template_mgmt.service import (
    InvalidDocxFileError,
    TemplateService,
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


def test_create_and_get_native_template(db_session):
    tpl_in = TemplateCreate(
        name="Informe Ejecutivo Anual",
        description="Plantilla estándar para informes corporativos",
        source_type="native",
        sections=[
            SectionSchema(
                id="sec_resumen",
                title="Resumen Ejecutivo",
                position=0,
                required=True,
                instructions="Sintetizar los hallazgos principales en 2 párrafos.",
            ),
            SectionSchema(
                id="sec_resultados",
                title="Resultados Clave",
                position=1,
                required=True,
                instructions="Detallar métricas financieras y operativas.",
                depends_on=["sec_resumen"],
            ),
        ],
    )

    created = TemplateService.create_template(db_session, tpl_in)
    assert created.id is not None
    assert created.name == "Informe Ejecutivo Anual"
    assert len(created.sections) == 2
    assert created.sections[1]["depends_on"] == ["sec_resumen"]

    fetched = TemplateService.get_template(db_session, created.id)
    assert fetched.id == created.id
    assert fetched.name == created.name


def test_update_template_sections(db_session):
    tpl = TemplateService.create_template(
        db_session,
        TemplateCreate(name="Borrador", sections=[]),
    )

    update_in = TemplateUpdate(
        name="Plantilla Actualizada",
        sections=[
            SectionSchema(
                id="sec_1",
                title="Sección Nueva",
                position=0,
                required=True,
                instructions="Instrucciones actualizadas",
            )
        ],
    )

    updated = TemplateService.update_template(db_session, tpl.id, update_in)
    assert updated.name == "Plantilla Actualizada"
    assert len(updated.sections) == 1
    assert updated.sections[0]["title"] == "Sección Nueva"


def test_create_document_from_template(db_session):
    tpl = TemplateService.create_template(
        db_session,
        TemplateCreate(
            name="Propuesta Comercial",
            sections=[
                SectionSchema(
                    id="sec_intro",
                    title="1. Introducción",
                    position=0,
                    required=True,
                    instructions="Presentar a la empresa cliente",
                ),
                SectionSchema(
                    id="sec_alcance",
                    title="2. Alcance del Proyecto",
                    position=1,
                    required=True,
                    instructions="Definir entregables específicos",
                ),
            ],
        ),
    )

    doc = TemplateService.create_document_from_template(db_session, tpl.id)
    assert doc.id is not None
    assert "Propuesta Comercial" in doc.title
    assert doc.template_id == tpl.id
    assert doc.version == 1

    content = doc.content
    assert content["type"] == "doc"
    # Debe tener al menos 4 nodos: 2 headings y 2 párrafos con instrucciones
    nodes = content["content"]
    assert len(nodes) >= 4
    assert nodes[0]["type"] == "heading"
    assert nodes[0]["content"][0]["text"] == "1. Introducción"
    assert nodes[1]["type"] == "paragraph"
    assert "Presentar a la empresa cliente" in nodes[1]["content"][0]["text"]


def test_import_and_inspect_docx(db_session):
    # Generar un DOCX válido en memoria con python-docx
    docx_buf = io.BytesIO()
    doc = DocxWriter()
    doc.add_heading("Antecedentes del Proyecto", level=1)
    doc.add_paragraph("Este es el texto del párrafo de antecedentes.")
    doc.add_heading("Objetivos Generales", level=1)
    doc.add_paragraph("Este es el texto de objetivos.")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Item"
    table.cell(0, 1).text = "Valor"
    doc.save(docx_buf)
    file_bytes = docx_buf.getvalue()

    result = TemplateService.import_and_inspect_docx(
        db_session, file_bytes, "Documento_Institucional.docx"
    )

    assert result.template_id is not None
    assert result.headings_count == 2
    assert result.tables_count == 1
    assert len(result.detected_sections) == 2
    assert result.detected_sections[0].title == "Antecedentes del Proyecto"
    assert result.detected_sections[1].title == "Objetivos Generales"

    # Verificar que la plantilla quedó persistida en BD
    tpl = TemplateService.get_template(db_session, result.template_id)
    assert tpl.source_type == "docx"
    assert tpl.source_file_id is not None

    # Limpiar archivo generado en storage
    TemplateService.delete_template(db_session, tpl.id)


def test_import_invalid_file_extension(db_session):
    with pytest.raises(InvalidDocxFileError) as exc_info:
        TemplateService.import_and_inspect_docx(db_session, b"fake", "archivo.pdf")
    assert "extensión .docx" in str(exc_info.value)
