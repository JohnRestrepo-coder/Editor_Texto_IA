from typing import Any

from backend.app.modules.document_mgmt.schemas import DocumentContent, Node

ALLOWED_NODE_TYPES = {
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
    "aiBlock",
}

ALLOWED_MARKS = {"bold", "italic", "underline"}


class OutputValidator:
    """
    Validador estricto de salidas estructuradas de modelos de lenguaje.
    Garantiza que la respuesta contenga únicamente nodos y atributos válidos de Tiptap,
    previniendo inyección de scripts, etiquetas HTML arbitrarias o esquemas rotos.
    """

    @classmethod
    def validate_and_sanitize(cls, raw_content: Any) -> DocumentContent:
        if not isinstance(raw_content, dict):
            raise TypeError("El contenido generado debe ser un objeto JSON (dict).")

        # Asegurar tipo doc
        content_type = raw_content.get("type", "doc")
        if content_type != "doc":
            raw_content["type"] = "doc"

        nodes = raw_content.get("content", [])
        if not isinstance(nodes, list):
            raise TypeError("La propiedad 'content' debe ser una lista de nodos.")

        sanitized_nodes: list[Node] = []
        for node_data in nodes:
            validated_node = cls._validate_node(node_data)
            if validated_node:
                sanitized_nodes.append(validated_node)

        if not sanitized_nodes:
            # Fallback seguro: párrafo con texto
            sanitized_nodes.append(
                Node(type="paragraph", content=[Node(type="text", text="")])
            )

        return DocumentContent(type="doc", content=sanitized_nodes)

    @classmethod
    def _validate_node(cls, node_data: Any) -> Node | None:
        if not isinstance(node_data, dict):
            return None

        node_type = node_data.get("type")
        if node_type not in ALLOWED_NODE_TYPES:
            # Descartar nodos con tipos no permitidos
            return None

        # Si es un nodo de texto
        if node_type == "text":
            text_value = str(node_data.get("text", ""))
            marks = node_data.get("marks")
            valid_marks = None
            if isinstance(marks, list):
                valid_marks = [
                    m
                    for m in marks
                    if isinstance(m, dict) and m.get("type") in ALLOWED_MARKS
                ]
            return Node(type="text", text=text_value, marks=valid_marks)

        # Nodos contenedores
        attrs = node_data.get("attrs")
        if node_type == "heading" and isinstance(attrs, dict):
            level = attrs.get("level", 2)
            try:
                level = max(1, min(6, int(level)))
            except (ValueError, TypeError):
                level = 2
            attrs = {"level": level}

        children: list[Node] = []
        raw_children = node_data.get("content", [])
        if isinstance(raw_children, list):
            for child in raw_children:
                valid_child = cls._validate_node(child)
                if valid_child:
                    children.append(valid_child)

        return Node(type=node_type, attrs=attrs, content=children if children else None)
