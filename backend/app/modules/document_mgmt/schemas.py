from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# Marks schema
MarkType = Literal["bold", "italic", "underline", "strike", "link", "textStyle"]


class Mark(BaseModel):
    type: MarkType
    attrs: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


# Node schema
NodeType = Literal[
    "paragraph",
    "heading",
    "bulletList",
    "orderedList",
    "listItem",
    "blockquote",
    "horizontalRule",
    "table",
    "tableRow",
    "tableCell",
    "tableHeader",
    "text",
    "hardBreak",
    "image",
    "aiBlock",
]


class Node(BaseModel):
    type: NodeType
    attrs: dict[str, Any] | None = None
    content: list["Node"] | None = None
    text: str | None = None
    marks: list[Mark] | None = None

    model_config = ConfigDict(extra="forbid")


# Self-referencing model rebuild
Node.model_rebuild()


class DocumentContent(BaseModel):
    type: Literal["doc"] = "doc"
    content: list[Node] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


# API Schemas
class DocumentCreate(BaseModel):
    title: str = Field(default="Documento sin título", min_length=1, max_length=255)
    content: DocumentContent | None = None
    template_id: str | None = None


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: DocumentContent | None = None
    expected_version: int = Field(
        ...,
        description="Versión previa esperada para control optimista de concurrencia",
    )


class DocumentResponse(BaseModel):
    id: str
    title: str
    content: DocumentContent
    version: int
    template_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListItem(BaseModel):
    id: str
    title: str
    version: int
    template_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
