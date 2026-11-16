import html
from typing import Any

from backend.app.modules.export_engine.matrix import CompatibilityTracker


class HtmlRenderer:
    @classmethod
    def render_to_html(
        cls,
        doc_title: str,
        doc_content: dict[str, Any],
        tracker: CompatibilityTracker,
        is_preview: bool = False,
    ) -> str:
        body_html = cls._render_nodes(doc_content.get("content", []), tracker)

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>{html.escape(doc_title)}</title>
  <style>
    @page {{
      size: A4;
      margin: 2.5cm 2cm 2.5cm 2cm;
      @bottom-right {{
        content: counter(page);
      }}
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 11pt;
      line-height: 1.6;
      color: #1e293b;
      margin: {"20px auto; max-width: 800px; background: white; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);" if is_preview else "0;"}
    }}
    h1 {{
      font-size: 22pt;
      font-weight: 700;
      color: #0f172a;
      margin-top: 0;
      margin-bottom: 24px;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 12px;
      page-break-after: avoid;
    }}
    h2 {{
      font-size: 15pt;
      font-weight: 600;
      color: #1e293b;
      margin-top: 24px;
      margin-bottom: 12px;
      page-break-after: avoid;
    }}
    h3 {{
      font-size: 13pt;
      font-weight: 600;
      color: #334155;
      margin-top: 18px;
      margin-bottom: 8px;
      page-break-after: avoid;
    }}
    p {{
      margin-top: 0;
      margin-bottom: 12px;
      text-align: justify;
    }}
    ul, ol {{
      margin-top: 0;
      margin-bottom: 12px;
      padding-left: 24px;
    }}
    li {{
      margin-bottom: 4px;
    }}
    blockquote {{
      margin: 16px 0;
      padding: 8px 16px;
      border-left: 4px solid #6366f1;
      background-color: #f8fafc;
      font-style: italic;
      color: #475569;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      page-break-inside: avoid;
    }}
    th, td {{
      border: 1px solid #cbd5e1;
      padding: 8px 12px;
      text-align: left;
      font-size: 10pt;
    }}
    th {{
      background-color: #f1f5f9;
      font-weight: 600;
      color: #0f172a;
    }}
    .document-title {{
      font-size: 24pt;
      font-weight: 800;
      color: #1e1b4b;
      margin-bottom: 20px;
    }}
  </style>
</head>
<body>
  <div class="document-title">{html.escape(doc_title)}</div>
  {body_html}
</body>
</html>"""

    @classmethod
    def _render_nodes(
        cls, nodes: list[dict[str, Any]], tracker: CompatibilityTracker
    ) -> str:
        if not isinstance(nodes, list):
            return ""

        parts: list[str] = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            tracker.check_node(node)
            node_type = node.get("type")

            if node_type == "heading":
                attrs = node.get("attrs", {})
                level = attrs.get("level", 2)
                try:
                    level = max(1, min(6, int(level)))
                except (ValueError, TypeError):
                    level = 2
                inner = cls._render_inlines(node.get("content", []), tracker)
                parts.append(f"<h{level}>{inner}</h{level}>")

            elif node_type == "paragraph":
                inner = cls._render_inlines(node.get("content", []), tracker)
                parts.append(f"<p>{inner or '&nbsp;'}</p>")

            elif node_type == "bulletList":
                items_html = []
                for item in node.get("content", []):
                    if isinstance(item, dict) and item.get("type") == "listItem":
                        item_inner = cls._render_nodes(item.get("content", []), tracker)
                        items_html.append(f"<li>{item_inner}</li>")
                parts.append(f"<ul>{''.join(items_html)}</ul>")

            elif node_type == "orderedList":
                items_html = []
                for item in node.get("content", []):
                    if isinstance(item, dict) and item.get("type") == "listItem":
                        item_inner = cls._render_nodes(item.get("content", []), tracker)
                        items_html.append(f"<li>{item_inner}</li>")
                parts.append(f"<ol>{''.join(items_html)}</ol>")

            elif node_type == "blockquote":
                inner = cls._render_inlines(node.get("content", []), tracker)
                parts.append(f"<blockquote>{inner}</blockquote>")

            elif node_type == "table":
                parts.append(cls._render_table(node, tracker))

        return "\n".join(parts)

    @classmethod
    def _render_inlines(
        cls, inlines: list[dict[str, Any]], tracker: CompatibilityTracker
    ) -> str:
        if not isinstance(inlines, list):
            return ""

        parts: list[str] = []
        for inline in inlines:
            if not isinstance(inline, dict):
                continue
            tracker.check_node(inline)

            if inline.get("type") == "text":
                text = html.escape(str(inline.get("text", "")))
                marks = inline.get("marks", [])
                if isinstance(marks, list):
                    for mark in marks:
                        if isinstance(mark, dict):
                            m_type = mark.get("type")
                            if m_type == "bold":
                                text = f"<strong>{text}</strong>"
                            elif m_type == "italic":
                                text = f"<em>{text}</em>"
                            elif m_type == "underline":
                                text = f"<u>{text}</u>"
                parts.append(text)
            elif inline.get("type") == "paragraph":
                parts.append(cls._render_inlines(inline.get("content", []), tracker))

        return "".join(parts)

    @classmethod
    def _render_table(
        cls, table_node: dict[str, Any], tracker: CompatibilityTracker
    ) -> str:
        rows_data = table_node.get("content", [])
        if not isinstance(rows_data, list) or not rows_data:
            return ""

        rows_html = []
        for r_idx, row in enumerate(rows_data):
            if not isinstance(row, dict):
                continue
            cells_html = []
            for cell in row.get("content", []):
                if not isinstance(cell, dict):
                    continue
                tag = "th" if r_idx == 0 or cell.get("type") == "tableHeader" else "td"
                cell_content = cls._render_inlines(cell.get("content", []), tracker)
                cells_html.append(f"<{tag}>{cell_content}</{tag}>")
            rows_html.append(f"<tr>{''.join(cells_html)}</tr>")

        return f"<table>{''.join(rows_html)}</table>"
