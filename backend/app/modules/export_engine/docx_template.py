import io
import os
from typing import Any

from docx import Document
from docxtpl import DocxTemplate

from backend.app.config import settings
from backend.app.modules.export_engine.docx_native import NativeDocxExporter
from backend.app.modules.export_engine.matrix import CompatibilityTracker
from backend.app.modules.template_mgmt.models import TemplateModel


class TemplateDocxExporter:
    @classmethod
    def export(
        cls,
        doc_title: str,
        doc_content: dict[str, Any],
        template: TemplateModel,
        tracker: CompatibilityTracker,
    ) -> bytes:
        if not template.source_file_id:
            # Si la plantilla no tiene archivo importado, exportar como nativo
            return NativeDocxExporter.export(doc_title, doc_content, tracker)

        template_path = os.path.join(
            settings.STORAGE_DIR, "templates", f"{template.source_file_id}.docx"
        )

        if not os.path.exists(template_path):
            tracker.unsupported_elements.append(
                f"Archivo original de plantilla {template.source_file_id}.docx no encontrado en almacenamiento. Se generó formato nativo."
            )
            return NativeDocxExporter.export(doc_title, doc_content, tracker)

        # 1. Relleno con docxtpl para variables Jinja {{ ... }}
        context_vars = cls._build_context_vars(doc_title, doc_content, template)

        try:
            tpl_doc = DocxTemplate(template_path)
            tpl_doc.render(context_vars)

            intermediate_buffer = io.BytesIO()
            tpl_doc.save(intermediate_buffer)
            intermediate_buffer.seek(0)
        except (ValueError, KeyError, TypeError, OSError) as e:
            tracker.unsupported_elements.append(
                f"Advertencia al procesar etiquetas docxtpl: {e}. Se utilizó documento base directo."
            )
            with open(template_path, "rb") as f:
                intermediate_buffer = io.BytesIO(f.read())
            intermediate_buffer.seek(0)

        # 2. Inyectar / Añadir los bloques de contenido estructurados respetando la plantilla
        docx = Document(intermediate_buffer)

        # Extraer nodos del documento Tiptap
        nodes = doc_content.get("content", []) if isinstance(doc_content, dict) else []

        # Agregamos los bloques al final del documento plantilla conservando sus estilos
        for node in nodes:
            if not isinstance(node, dict):
                continue
            tracker.check_node(node)
            NativeDocxExporter._render_node(docx, node, tracker)

        output_buffer = io.BytesIO()
        docx.save(output_buffer)
        output_buffer.seek(0)
        return output_buffer.getvalue()

    @classmethod
    def _build_context_vars(
        cls, doc_title: str, doc_content: dict[str, Any], template: TemplateModel
    ) -> dict[str, Any]:
        vars_dict: dict[str, Any] = {
            "title": doc_title,
            "document_title": doc_title,
            "template_name": template.name,
        }

        # Extraer textos por sección si coinciden con los nombres de sección
        if isinstance(doc_content, dict) and "content" in doc_content:
            nodes = doc_content.get("content", [])
            current_sec = None
            current_texts: list[str] = []

            for n in nodes:
                if isinstance(n, dict):
                    if n.get("type") == "heading":
                        if current_sec and current_texts:
                            clean_key = current_sec.lower().replace(" ", "_")
                            vars_dict[clean_key] = "\n".join(current_texts)
                            current_texts = []
                        title_parts = [
                            c.get("text", "")
                            for c in n.get("content", [])
                            if isinstance(c, dict)
                        ]
                        current_sec = "".join(title_parts).strip()
                    elif n.get("type") == "paragraph":
                        p_parts = [
                            c.get("text", "")
                            for c in n.get("content", [])
                            if isinstance(c, dict)
                        ]
                        current_texts.append("".join(p_parts))

            if current_sec and current_texts:
                clean_key = current_sec.lower().replace(" ", "_")
                vars_dict[clean_key] = "\n".join(current_texts)

        return vars_dict
