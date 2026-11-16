import os
import uuid

from docx import Document as DocxReader
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.modules.document_mgmt.models import DocumentModel
from backend.app.modules.document_mgmt.schemas import (
    DocumentContent,
    DocumentCreate,
    Node,
)
from backend.app.modules.document_mgmt.service import DocumentService
from backend.app.modules.template_mgmt.models import TemplateModel
from backend.app.modules.template_mgmt.schemas import (
    DocxInspectionResult,
    SectionSchema,
    TemplateCreate,
    TemplateListItem,
    TemplateUpdate,
)


class TemplateNotFoundError(Exception):
    pass


class InvalidDocxFileError(Exception):
    pass


class TemplateService:
    @classmethod
    def create_template(cls, db: Session, tpl_in: TemplateCreate) -> TemplateModel:
        sections_data = [sec.model_dump() for sec in tpl_in.sections]
        tpl = TemplateModel(
            name=tpl_in.name,
            description=tpl_in.description,
            source_type=tpl_in.source_type,
            source_file_id=tpl_in.source_file_id,
            language=tpl_in.language,
            sections=sections_data,
            style_profile=tpl_in.style_profile,
        )
        db.add(tpl)
        db.commit()
        db.refresh(tpl)
        return tpl

    @classmethod
    def get_template(cls, db: Session, template_id: str) -> TemplateModel:
        tpl = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
        if not tpl:
            raise TemplateNotFoundError(f"Plantilla '{template_id}' no encontrada")
        return tpl

    @classmethod
    def list_templates(
        cls, db: Session, limit: int = 50, offset: int = 0
    ) -> list[TemplateListItem]:
        rows = (
            db.query(TemplateModel)
            .order_by(desc(TemplateModel.updated_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [
            TemplateListItem(
                id=r.id,
                name=r.name,
                description=r.description,
                source_type=r.source_type,  # type: ignore
                sections_count=len(r.sections) if r.sections else 0,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in rows
        ]

    @classmethod
    def update_template(
        cls, db: Session, template_id: str, tpl_in: TemplateUpdate
    ) -> TemplateModel:
        tpl = cls.get_template(db, template_id)

        if tpl_in.name is not None:
            tpl.name = tpl_in.name
        if tpl_in.description is not None:
            tpl.description = tpl_in.description
        if tpl_in.language is not None:
            tpl.language = tpl_in.language
        if tpl_in.sections is not None:
            tpl.sections = [sec.model_dump() for sec in tpl_in.sections]
        if tpl_in.style_profile is not None:
            tpl.style_profile = tpl_in.style_profile

        db.commit()
        db.refresh(tpl)
        return tpl

    @classmethod
    def delete_template(cls, db: Session, template_id: str) -> None:
        tpl = cls.get_template(db, template_id)

        # Si tiene archivo DOCX asociado, eliminarlo de storage de forma segura
        if tpl.source_file_id:
            file_path = os.path.join(
                settings.STORAGE_DIR, "templates", tpl.source_file_id
            )
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

        db.delete(tpl)
        db.commit()

    @classmethod
    def import_and_inspect_docx(
        cls, db: Session, file_content: bytes, filename: str
    ) -> DocxInspectionResult:
        if not filename.lower().endswith(".docx"):
            raise InvalidDocxFileError("El archivo debe tener extensión .docx válida")

        # Validar tamaño máximo (ej. 20 MB)
        if len(file_content) > 20 * 1024 * 1024:
            raise InvalidDocxFileError(
                "El archivo excede el tamaño máximo permitido de 20MB"
            )

        # Guardar binario original preservado
        file_uuid = f"{uuid.uuid4()}.docx"
        target_dir = os.path.join(settings.STORAGE_DIR, "templates")
        os.makedirs(target_dir, exist_ok=True)
        saved_path = os.path.join(target_dir, file_uuid)

        with open(saved_path, "wb") as f:
            f.write(file_content)

        # Inspección con python-docx
        try:
            doc = DocxReader(saved_path)
        except Exception as e:  # noqa: BLE001
            if os.path.exists(saved_path):
                os.remove(saved_path)
            raise InvalidDocxFileError(f"No se pudo leer el archivo Word: {e!s}")

        detected_sections: list[SectionSchema] = []
        headings_count = 0
        paragraphs_count = len(doc.paragraphs)
        tables_count = len(doc.tables)
        unsupported_elements: list[str] = []

        # Analizar párrafos en busca de encabezados
        position = 0
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue

            style_name = (p.style.name if p.style else "").lower()
            if (
                "heading" in style_name
                or "encabezado" in style_name
                or "título" in style_name
            ):
                headings_count += 1
                sec_id = f"sec_{uuid.uuid4().hex[:8]}"
                detected_sections.append(
                    SectionSchema(
                        id=sec_id,
                        title=text,
                        position=position,
                        required=True,
                        instructions=f"Contenido estructurado para la sección: {text}",
                        generation_enabled=True,
                        depends_on=[],
                    )
                )
                position += 1

        # Si no se detectaron encabezados explícitos, sugerir secciones por párrafos significativos
        if not detected_sections:
            for p in doc.paragraphs[:10]:
                text = p.text.strip()
                if len(text) > 0 and len(text) <= 100:
                    sec_id = f"sec_{uuid.uuid4().hex[:8]}"
                    detected_sections.append(
                        SectionSchema(
                            id=sec_id,
                            title=text,
                            position=position,
                            required=True,
                            instructions=f"Párrafo de plantilla: {text}",
                            generation_enabled=True,
                            depends_on=[],
                        )
                    )
                    position += 1

        # Si aún no hay secciones, crear una sección por defecto
        if not detected_sections:
            detected_sections.append(
                SectionSchema(
                    id="sec_default",
                    title="Contenido General",
                    position=0,
                    required=True,
                    instructions="Redactar el cuerpo del documento a partir de la plantilla DOCX",
                    generation_enabled=True,
                    depends_on=[],
                )
            )

        # Registrar advertencias sobre elementos complejos si existen
        if tables_count > 0:
            unsupported_elements.append(
                f"Detectadas {tables_count} tablas en el documento; se conservarán en el archivo original pero requieren verificación visual."
            )

        clean_name = os.path.splitext(filename)[0].replace("_", " ").title()

        # Crear plantilla inicial en la base de datos
        tpl = cls.create_template(
            db,
            TemplateCreate(
                name=clean_name,
                description=f"Plantilla importada desde archivo Word '{filename}' con {len(detected_sections)} secciones detectadas.",
                source_type="docx",
                source_file_id=file_uuid,
                language="es",
                sections=detected_sections,
                style_profile={
                    "original_filename": filename,
                    "tables_count": tables_count,
                },
            ),
        )

        return DocxInspectionResult(
            template_id=tpl.id,
            filename=filename,
            source_file_id=file_uuid,
            detected_sections=detected_sections,
            headings_count=headings_count,
            paragraphs_count=paragraphs_count,
            tables_count=tables_count,
            unsupported_elements=unsupported_elements,
        )

    @classmethod
    def create_document_from_template(
        cls, db: Session, template_id: str
    ) -> DocumentModel:
        tpl = cls.get_template(db, template_id)

        # Construir contenido inicial Tiptap ordenado por secciones
        nodes: list[Node] = []

        sorted_sections = sorted(
            [SectionSchema(**sec) for sec in tpl.sections],
            key=lambda s: s.position,
        )

        for sec in sorted_sections:
            # Encabezado de la sección
            nodes.append(
                Node(
                    type="heading",
                    attrs={"level": 2},
                    content=[Node(type="text", text=sec.title)],
                )
            )
            # Párrafo guía con instrucciones
            instructions_text = (
                f"[Instrucción: {sec.instructions}]"
                if sec.instructions
                else "Escribe el contenido de esta sección..."
            )
            nodes.append(
                Node(
                    type="paragraph",
                    content=[Node(type="text", text=instructions_text)],
                )
            )

        if not nodes:
            nodes.append(Node(type="paragraph", content=[]))

        doc_content = DocumentContent(type="doc", content=nodes)

        # Instanciar documento libre enlazado a la plantilla
        doc_in = DocumentCreate(
            title=f"Nuevo Documento — {tpl.name}",
            content=doc_content,
            template_id=tpl.id,
        )

        return DocumentService.create_document(db, doc_in)
