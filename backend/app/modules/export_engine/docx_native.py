import io
from typing import Any

from docx import Document
from docx.shared import Inches, Pt, RGBColor

from backend.app.modules.export_engine.matrix import CompatibilityTracker


class NativeDocxExporter:
    @classmethod
    def export(
        cls, doc_title: str, doc_content: dict[str, Any], tracker: CompatibilityTracker
    ) -> bytes:
        docx = Document()

        # Configurar márgenes estándar (1 pulgada / 2.54 cm)
        for section in docx.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

        # Título principal del documento
        title_p = docx.add_paragraph()
        run = title_p.add_run(doc_title)
        run.font.size = Pt(22)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)  # Slate 800

        nodes = doc_content.get("content", []) if isinstance(doc_content, dict) else []

        for node in nodes:
            if not isinstance(node, dict):
                continue
            tracker.check_node(node)
            cls._render_node(docx, node, tracker)

        buffer = io.BytesIO()
        docx.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def _render_node(
        cls, docx: Document, node: dict[str, Any], tracker: CompatibilityTracker
    ) -> None:
        node_type = node.get("type")

        if node_type == "heading":
            attrs = node.get("attrs", {})
            level = attrs.get("level", 2)
            try:
                level = max(1, min(6, int(level)))
            except (ValueError, TypeError):
                level = 2
            p = docx.add_heading(level=level)
            cls._add_inline_runs(p, node.get("content", []), tracker)

        elif node_type == "paragraph":
            p = docx.add_paragraph()
            cls._add_inline_runs(p, node.get("content", []), tracker)

        elif node_type == "bulletList":
            for item in node.get("content", []):
                if isinstance(item, dict) and item.get("type") == "listItem":
                    for child in item.get("content", []):
                        if isinstance(child, dict):
                            p = docx.add_paragraph(style="List Bullet")
                            cls._add_inline_runs(p, child.get("content", []), tracker)

        elif node_type == "orderedList":
            for item in node.get("content", []):
                if isinstance(item, dict) and item.get("type") == "listItem":
                    for child in item.get("content", []):
                        if isinstance(child, dict):
                            p = docx.add_paragraph(style="List Number")
                            cls._add_inline_runs(p, child.get("content", []), tracker)

        elif node_type == "blockquote":
            p = docx.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.5)
            cls._add_inline_runs(p, node.get("content", []), tracker, force_italic=True)

        elif node_type == "table":
            cls._render_table(docx, node, tracker)

        elif node_type == "aiBlock":
            attrs = node.get("attrs", {})
            title = attrs.get("sectionTitle") or "Bloque de IA"
            instructions = attrs.get("instructions") or ""
            p = docx.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            run = p.add_run(
                f"[🤖 {title}"
                + (f" — Instrucción: {instructions}" if instructions else "")
                + "]"
            )
            run.italic = True
            run.font.color.rgb = RGBColor(0x63, 0x66, 0xF1)

    @classmethod
    def _add_inline_runs(
        cls,
        paragraph: Any,
        inline_nodes: list[dict[str, Any]],
        tracker: CompatibilityTracker,
        force_italic: bool = False,
    ) -> None:
        if not isinstance(inline_nodes, list):
            return

        for inline in inline_nodes:
            if not isinstance(inline, dict):
                continue

            tracker.check_node(inline)

            if inline.get("type") == "text":
                text = str(inline.get("text", ""))
                run = paragraph.add_run(text)

                if force_italic:
                    run.italic = True

                marks = inline.get("marks", [])
                if isinstance(marks, list):
                    for mark in marks:
                        if not isinstance(mark, dict):
                            continue
                        m_type = mark.get("type")
                        if m_type == "bold":
                            run.bold = True
                        elif m_type == "italic":
                            run.italic = True
                        elif m_type == "underline":
                            run.underline = True

            elif inline.get("type") == "paragraph":
                cls._add_inline_runs(
                    paragraph, inline.get("content", []), tracker, force_italic
                )

    @classmethod
    def _render_table(
        cls, docx: Document, table_node: dict[str, Any], tracker: CompatibilityTracker
    ) -> None:
        rows_data = table_node.get("content", [])
        if not isinstance(rows_data, list) or not rows_data:
            return

        num_rows = len(rows_data)
        num_cols = 0
        first_row = rows_data[0]
        if isinstance(first_row, dict) and "content" in first_row:
            num_cols = len(first_row.get("content", []))

        if num_cols == 0:
            return

        table = docx.add_table(rows=num_rows, cols=num_cols)
        table.style = "Table Grid"

        for r_idx, row in enumerate(rows_data):
            if not isinstance(row, dict):
                continue
            cells_data = row.get("content", [])
            for c_idx, cell in enumerate(cells_data):
                if c_idx >= num_cols or not isinstance(cell, dict):
                    continue
                docx_cell = table.cell(r_idx, c_idx)
                # Limpiar párrafos por defecto en celda
                docx_cell.text = ""
                p = docx_cell.paragraphs[0]
                for p_child in cell.get("content", []):
                    if isinstance(p_child, dict):
                        cls._add_inline_runs(p, p_child.get("content", []), tracker)
