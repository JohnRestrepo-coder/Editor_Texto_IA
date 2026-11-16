from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# Marks schema
MarkType = Literal["bold", "italic", "underline", "strike", "link", "textStyle"]

class Mark(BaseModel):
    type: MarkType
    attrs: Optional[Dict[str, Any]] = None

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
    "text",
    "hardBreak",
    "image"
]

class Node(BaseModel):
    type: NodeType
    attrs: Optional[Dict[str, Any]] = None
    content: Optional[List["Node"]] = None
    text: Optional[str] = None
    marks: Optional[List[Mark]] = None

    model_config = ConfigDict(extra="forbid")

# Self-referencing model rebuild
Node.model_rebuild()

class DocumentContent(BaseModel):
    type: Literal["doc"] = "doc"
    content: List[Node] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

# API Schemas
class DocumentCreate(BaseModel):
    title: str = Field(default="Documento sin título", min_length=1, max_length=255)
    content: Optional[DocumentContent] = None
    template_id: Optional[str] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    content: Optional[DocumentContent] = None
    expected_version: int = Field(..., description="Versión previa esperada para control optimista de concurrencia")

class DocumentResponse(BaseModel):
    id: str
    title: str
    content: DocumentContent
    version: int
    template_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentListItem(BaseModel):
    id: str
    title: str
    version: int
    template_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
