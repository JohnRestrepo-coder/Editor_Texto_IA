import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.document_mgmt.models import DocumentModel
from backend.app.modules.export_engine.docx_native import NativeDocxExporter
from backend.app.modules.export_engine.docx_template import TemplateDocxExporter
from backend.app.modules.export_engine.html_renderer import HtmlRenderer
from backend.app.modules.export_engine.matrix import CompatibilityTracker
from backend.app.modules.export_engine.pdf_exporter import PdfExporter
from backend.app.modules.template_mgmt.models import TemplateModel


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned.replace(" ", "_") or "documento"


class ExportService:
    @classmethod
    def export_docx(cls, db: Session, document_id: str) -> tuple[bytes, str, list[str]]:
        document = (
            db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {document_id} no encontrado.",
            )

        tracker = CompatibilityTracker()
        filename = f"{sanitize_filename(document.title)}.docx"

        # Si el documento está asociado a una plantilla importada
        if document.template_id:
            template = (
                db.query(TemplateModel)
                .filter(TemplateModel.id == document.template_id)
                .first()
            )
            if template:
                docx_bytes = TemplateDocxExporter.export(
                    doc_title=document.title,
                    doc_content=document.content,
                    template=template,
                    tracker=tracker,
                )
                return docx_bytes, filename, tracker.unsupported_elements

        # Exportación nativa estándar
        docx_bytes = NativeDocxExporter.export(
            doc_title=document.title,
            doc_content=document.content,
            tracker=tracker,
        )
        return docx_bytes, filename, tracker.unsupported_elements

    @classmethod
    def export_pdf(cls, db: Session, document_id: str) -> tuple[bytes, str, list[str]]:
        document = (
            db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {document_id} no encontrado.",
            )

        tracker = CompatibilityTracker()
        filename = f"{sanitize_filename(document.title)}.pdf"

        try:
            pdf_bytes = PdfExporter.export(
                doc_title=document.title,
                doc_content=document.content,
                tracker=tracker,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error durante el renderizado PDF con Playwright: {e}",
            ) from e

        return pdf_bytes, filename, tracker.unsupported_elements

    @classmethod
    def render_html_preview(cls, db: Session, document_id: str) -> str:
        document = (
            db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {document_id} no encontrado.",
            )

        tracker = CompatibilityTracker()
        return HtmlRenderer.render_to_html(
            doc_title=document.title,
            doc_content=document.content,
            tracker=tracker,
            is_preview=True,
        )
