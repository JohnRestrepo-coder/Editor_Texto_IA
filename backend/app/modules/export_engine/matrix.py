from typing import Any

SUPPORTED_NODES = {
    "doc",
    "paragraph",
    "heading",
    "bulletList",
    "orderedList",
    "listItem",
    "blockquote",
    "text",
    "table",
    "tableRow",
    "tableCell",
    "tableHeader",
}

SUPPORTED_MARKS = {"bold", "italic", "underline"}


class CompatibilityTracker:
    def __init__(self):
        self.unsupported_elements: list[str] = []

    def check_node(self, node: dict[str, Any]) -> bool:
        node_type = node.get("type", "unknown")
        if node_type not in SUPPORTED_NODES:
            msg = f"Nodo no soportado omitido o simplificado: '{node_type}'"
            if msg not in self.unsupported_elements:
                self.unsupported_elements.append(msg)
            return False

        marks = node.get("marks", [])
        if isinstance(marks, list):
            for m in marks:
                if isinstance(m, dict):
                    mark_type = m.get("type")
                    if mark_type and mark_type not in SUPPORTED_MARKS:
                        warn = f"Marca de estilo no soportada: '{mark_type}'"
                        if warn not in self.unsupported_elements:
                            self.unsupported_elements.append(warn)

        return True
