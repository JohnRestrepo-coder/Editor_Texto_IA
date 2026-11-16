from typing import Any

from backend.app.modules.document_mgmt.models import DocumentModel
from backend.app.modules.template_mgmt.models import TemplateModel


class ContextManager:
    """
    Recuperación contextual selectiva para la generación de secciones.
    Evita enviar todo el documento indiscriminadamente, seleccionando únicamente
    resúmenes pertinentes de secciones previas y pautas de la plantilla.
    """

    @classmethod
    def get_selective_context(
        cls,
        document: DocumentModel,
        section_id: str,
        section_title: str,
        template: TemplateModel | None = None,
        max_summary_words_per_section: int = 120,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {
            "document_title": document.title,
            "section_id": section_id,
            "section_title": section_title,
            "preceding_summary": "",
            "guidelines": "",
            "dependencies": [],
        }

        # Extraer pautas y dependencias si el documento proviene de una plantilla
        if template and isinstance(template.sections, list):
            for sec in template.sections:
                if sec.get("id") == section_id or sec.get("title") == section_title:
                    context["guidelines"] = sec.get("instructions", "")
                    context["dependencies"] = sec.get("depends_on", [])
                    break

        # Extraer resumen de texto previo en el documento
        doc_content = document.content
        if isinstance(doc_content, dict) and "content" in doc_content:
            nodes = doc_content["content"]
            summaries: list[str] = []
            current_sec_title = None
            current_sec_texts: list[str] = []

            for node in nodes:
                if not isinstance(node, dict):
                    continue

                if node.get("type") == "heading":
                    # Si ya teníamos una sección previa acumulada
                    if current_sec_title and current_sec_texts:
                        combined = " ".join(current_sec_texts).strip()
                        words = combined.split()
                        truncated = " ".join(words[:max_summary_words_per_section])
                        summaries.append(f"[{current_sec_title}]: {truncated}...")
                        current_sec_texts = []

                    heading_text = cls._extract_text(node)
                    # Si llegamos a la sección objetivo, detenemos la acumulación previa
                    if heading_text.strip().lower() == section_title.strip().lower():
                        break
                    current_sec_title = heading_text
                else:
                    text = cls._extract_text(node)
                    if text:
                        current_sec_texts.append(text)

            if summaries:
                context["preceding_summary"] = "\n".join(
                    summaries[-3:]
                )  # Últimas 3 secciones previas

        return context

    @classmethod
    def _extract_text(cls, node: dict[str, Any]) -> str:
        if node.get("type") == "text":
            return str(node.get("text", ""))

        content = node.get("content")
        if isinstance(content, list):
            return " ".join(
                [
                    cls._extract_text(child)
                    for child in content
                    if isinstance(child, dict)
                ]
            )
        return ""
