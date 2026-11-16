from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from backend.app.modules.document_mgmt.models import DocumentModel
from backend.app.modules.document_mgmt.schemas import DocumentCreate, DocumentUpdate

class DocumentNotFoundError(Exception):
    pass

class VersionConflictError(Exception):
    def __init__(self, current_version: int, expected_version: int):
        super().__init__(
            f"Conflicto de versión: la versión actual es {current_version}, pero se esperaba {expected_version}."
        )
        self.current_version = current_version
        self.expected_version = expected_version

class DocumentService:
    @staticmethod
    def default_empty_content() -> dict:
        return {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": []
                }
            ]
        }

    @classmethod
    def create_document(cls, db: Session, doc_in: DocumentCreate) -> DocumentModel:
        content_dict = (
            doc_in.content.model_dump()
            if doc_in.content
            else cls.default_empty_content()
        )

        doc = DocumentModel(
            title=doc_in.title,
            content=content_dict,
            template_id=doc_in.template_id,
            version=1
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @classmethod
    def get_document(cls, db: Session, doc_id: str) -> DocumentModel:
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        if not doc:
            raise DocumentNotFoundError(f"Documento {doc_id} no encontrado")
        return doc

    @classmethod
    def list_documents(cls, db: Session, limit: int = 50, offset: int = 0) -> List[DocumentModel]:
        return (
            db.query(DocumentModel)
            .order_by(desc(DocumentModel.updated_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @classmethod
    def update_document(
        cls, db: Session, doc_id: str, doc_in: DocumentUpdate
    ) -> DocumentModel:
        doc = cls.get_document(db, doc_id)

        if doc.version != doc_in.expected_version:
            raise VersionConflictError(
                current_version=doc.version,
                expected_version=doc_in.expected_version
            )

        if doc_in.title is not None:
            doc.title = doc_in.title

        if doc_in.content is not None:
            doc.content = doc_in.content.model_dump()

        doc.version += 1

        db.commit()
        db.refresh(doc)
        return doc

    @classmethod
    def delete_document(cls, db: Session, doc_id: str) -> None:
        doc = cls.get_document(db, doc_id)
        db.delete(doc)
        db.commit()
