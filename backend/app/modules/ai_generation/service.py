import logging
from typing import Any

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.ai_generation.context import ContextManager
from backend.app.modules.ai_generation.models import GenerationModel
from backend.app.modules.ai_generation.prompts import PromptManager
from backend.app.modules.ai_generation.provider import LLMRequest, get_llm_provider
from backend.app.modules.ai_generation.schemas import (
    FullGenerationRequest,
    FullGenerationResponse,
    GenerationResponse,
    SectionGenerationRequest,
)
from backend.app.modules.ai_generation.validator import OutputValidator
from backend.app.modules.document_mgmt.models import DocumentModel
from backend.app.modules.document_mgmt.schemas import (
    DocumentContent,
    DocumentResponse,
    Node,
)
from backend.app.modules.template_mgmt.models import TemplateModel

logger = logging.getLogger(__name__)


class AIGenerationService:
    @classmethod
    def generate_section(
        cls, db: Session, req: SectionGenerationRequest
    ) -> GenerationResponse:
        document = (
            db.query(DocumentModel).filter(DocumentModel.id == req.document_id).first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {req.document_id} no encontrado.",
            )

        template = None
        if document.template_id:
            template = (
                db.query(TemplateModel)
                .filter(TemplateModel.id == document.template_id)
                .first()
            )

        # Determinar título de la sección
        section_title = req.section_title or req.section_id
        if template and isinstance(template.sections, list):
            for sec in template.sections:
                if sec.get("id") == req.section_id:
                    section_title = sec.get("title", section_title)
                    break

        # Capturar snapshot actual de la sección para diff/preview
        original_nodes = cls._extract_section_nodes(document.content, section_title)

        # Contexto selectivo
        context_data = ContextManager.get_selective_context(
            document=document,
            section_id=req.section_id,
            section_title=section_title,
            template=template,
        )

        guidelines = context_data.get("guidelines", "")

        # Construir prompts
        system_instruction = PromptManager.get_system_instruction()
        user_prompt = PromptManager.build_user_prompt(
            document_title=document.title,
            section_title=section_title,
            section_guidelines=guidelines,
            user_instructions=req.user_instructions,
            context_data=context_data,
        )

        # Invocar adaptador LLM
        provider = get_llm_provider()
        llm_req = LLMRequest(
            prompt=user_prompt,
            system_instruction=system_instruction,
            context={
                "section_title": section_title,
                "guidelines": guidelines,
            },
        )

        try:
            llm_res = provider.generate(llm_req)
            # Validar y sanear estructura Tiptap
            validated_doc = OutputValidator.validate_and_sanitize(llm_res.content_json)
            status_val = "completed"
            error_msg = None
            proposed_content = validated_doc.model_dump()
        except (ValueError, TypeError, KeyError, httpx.HTTPError) as e:
            logger.error(f"Error en generación con IA: {e}")
            status_val = "failed"
            error_msg = str(e)
            proposed_content = None
            llm_res = None

        # Guardar en base de datos para auditoría y trazabilidad
        generation_rec = GenerationModel(
            document_id=document.id,
            section_id=req.section_id,
            section_title=section_title,
            status=status_val,
            user_instructions=req.user_instructions,
            content=proposed_content,
            original_section_content={
                "content": [n.model_dump() for n in original_nodes]
            }
            if original_nodes
            else None,
            provider=llm_res.provider if llm_res else "unknown",
            model=llm_res.model if llm_res else "unknown",
            prompt_version=PromptManager.VERSION,
            latency_ms=llm_res.latency_ms if llm_res else 0,
            tokens_used=llm_res.tokens_used if llm_res else 0,
            error_message=error_msg,
        )

        db.add(generation_rec)
        db.commit()
        db.refresh(generation_rec)

        return cls._to_response(generation_rec)

    @classmethod
    def get_generation(cls, db: Session, generation_id: str) -> GenerationResponse:
        gen = (
            db.query(GenerationModel)
            .filter(GenerationModel.id == generation_id)
            .first()
        )
        if not gen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Propuesta {generation_id} no encontrada.",
            )
        return cls._to_response(gen)

    @classmethod
    def accept_generation(
        cls, db: Session, generation_id: str, expected_version: int | None = None
    ) -> DocumentResponse:
        gen = (
            db.query(GenerationModel)
            .filter(GenerationModel.id == generation_id)
            .first()
        )
        if not gen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Propuesta {generation_id} no encontrada.",
            )

        if gen.status not in ("completed", "queued", "processing"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La propuesta se encuentra en estado '{gen.status}' y no puede ser aceptada.",
            )

        document = (
            db.query(DocumentModel).filter(DocumentModel.id == gen.document_id).first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {gen.document_id} no encontrado.",
            )

        # Control de concurrencia optimista
        if expected_version is not None and document.version != expected_version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Conflicto de versión. Esperada: {expected_version}, actual: {document.version}",
            )

        # Aplicar el contenido de la propuesta al documento
        if not gen.content or not isinstance(gen.content.get("content"), list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La propuesta no contiene bloques válidos para aplicar.",
            )

        new_section_nodes = [Node(**n) for n in gen.content["content"]]
        updated_doc_content = cls._replace_section_nodes(
            doc_content=document.content,
            section_title=gen.section_title,
            new_nodes=new_section_nodes,
        )

        document.content = updated_doc_content.model_dump()
        document.version += 1
        gen.status = "accepted"

        db.commit()
        db.refresh(document)
        db.refresh(gen)

        return DocumentResponse.model_validate(document)

    @classmethod
    def reject_generation(cls, db: Session, generation_id: str) -> GenerationResponse:
        gen = (
            db.query(GenerationModel)
            .filter(GenerationModel.id == generation_id)
            .first()
        )
        if not gen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Propuesta {generation_id} no encontrada.",
            )

        gen.status = "rejected"
        db.commit()
        db.refresh(gen)

        return cls._to_response(gen)

    @classmethod
    def list_document_generations(
        cls, db: Session, document_id: str
    ) -> list[GenerationResponse]:
        gens = (
            db.query(GenerationModel)
            .filter(GenerationModel.document_id == document_id)
            .order_by(GenerationModel.created_at.desc())
            .all()
        )
        return [cls._to_response(g) for g in gens]

    @classmethod
    def orchestrate_full_generation(
        cls, db: Session, document_id: str, req: FullGenerationRequest
    ) -> FullGenerationResponse:
        document = (
            db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {document_id} no encontrado.",
            )

        if (
            req.expected_document_version is not None
            and document.version != req.expected_document_version
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Conflicto de versión. Esperada: {req.expected_document_version}, actual: {document.version}",
            )

        template = None
        if document.template_id:
            template = (
                db.query(TemplateModel)
                .filter(TemplateModel.id == document.template_id)
                .first()
            )

        sections_to_generate: list[dict[str, Any]] = []

        if template and isinstance(template.sections, list) and template.sections:
            # Ordenamiento topológico respetando depends_on y position
            sections_to_generate = cls._topological_sort_sections(template.sections)
        else:
            # Extraer secciones existentes del contenido del documento
            extracted = cls._extract_all_sections_from_doc(document.content)
            sections_to_generate = [
                {"id": f"sec-{idx}", "title": title, "instructions": ""}
                for idx, title in enumerate(extracted)
            ]

        results: list[GenerationResponse] = []
        for sec in sections_to_generate:
            sec_req = SectionGenerationRequest(
                document_id=document_id,
                section_id=sec.get("id", "sec-0"),
                section_title=sec.get("title", "Sección"),
                user_instructions=req.instructions or sec.get("instructions", ""),
            )
            gen_res = cls.generate_section(db, sec_req)
            results.append(gen_res)

        return FullGenerationResponse(
            document_id=document_id,
            total_sections=len(results),
            generations=results,
            status="completed",
        )

    # ------------------ Métodos Auxiliares ------------------

    @classmethod
    def _topological_sort_sections(
        cls, raw_sections: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Ordena las secciones respetando dependencias (depends_on).
        Si no hay dependencias explícitas o se detectan ciclos, recurre a position.
        """
        sec_map = {s.get("id"): s for s in raw_sections if s.get("id")}
        in_degree: dict[str, int] = {sid: 0 for sid in sec_map}
        adj_list: dict[str, list[str]] = {sid: [] for sid in sec_map}

        for sid, s in sec_map.items():
            deps = s.get("depends_on", [])
            for dep in deps:
                if dep in sec_map:
                    adj_list[dep].append(sid)
                    in_degree[sid] += 1

        queue = [sid for sid, deg in in_degree.items() if deg == 0]
        # Ordenar por position como desempate
        queue.sort(key=lambda x: sec_map[x].get("position", 0))

        ordered: list[dict[str, Any]] = []
        while queue:
            curr = queue.pop(0)
            ordered.append(sec_map[curr])
            for neighbor in adj_list[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
            queue.sort(key=lambda x: sec_map[x].get("position", 0))

        if len(ordered) < len(raw_sections):
            # En caso de ciclos o IDs faltantes, fallback al orden por position
            return sorted(raw_sections, key=lambda s: s.get("position", 0))

        return ordered

    @classmethod
    def _extract_all_sections_from_doc(cls, doc_content: Any) -> list[str]:
        if not isinstance(doc_content, dict) or "content" not in doc_content:
            return ["Contenido Principal"]
        headings: list[str] = []
        for node in doc_content.get("content", []):
            if isinstance(node, dict) and node.get("type") == "heading":
                title = ContextManager._extract_text(node).strip()
                if title:
                    headings.append(title)
        return headings or ["Contenido Principal"]

    @classmethod
    def _extract_section_nodes(cls, doc_content: Any, section_title: str) -> list[Node]:
        """Extrae los nodos de contenido pertenecientes a la sección indicada."""
        if not isinstance(doc_content, dict) or "content" not in doc_content:
            return []

        nodes = doc_content.get("content", [])
        section_nodes: list[Node] = []
        in_target_section = False

        for node_data in nodes:
            if not isinstance(node_data, dict):
                continue

            if node_data.get("type") == "heading":
                h_text = ContextManager._extract_text(node_data).strip().lower()
                if h_text == section_title.strip().lower():
                    in_target_section = True
                    continue
                elif in_target_section:
                    # Llegó al siguiente encabezado, terminamos
                    break

            if in_target_section:
                section_nodes.append(Node(**node_data))

        return section_nodes

    @classmethod
    def _replace_section_nodes(
        cls, doc_content: Any, section_title: str, new_nodes: list[Node]
    ) -> DocumentContent:
        """
        Reemplaza únicamente los nodos de la sección especificada en el árbol Tiptap,
        dejando todas las demás secciones 100% inalteradas.
        """
        if not isinstance(doc_content, dict) or "content" not in doc_content:
            # Si el documento estaba vacío, construimos encabezado y nuevos nodos
            final_nodes = [
                Node(
                    type="heading",
                    attrs={"level": 2},
                    content=[Node(type="text", text=section_title)],
                ),
                *new_nodes,
            ]
            return DocumentContent(type="doc", content=final_nodes)

        raw_nodes = doc_content.get("content", [])
        updated_nodes: list[Node] = []
        in_target_section = False
        section_found = False

        for node_data in raw_nodes:
            if not isinstance(node_data, dict):
                continue

            if node_data.get("type") == "heading":
                h_text = ContextManager._extract_text(node_data).strip().lower()
                if h_text == section_title.strip().lower():
                    in_target_section = True
                    section_found = True
                    # Mantener el encabezado de la sección
                    updated_nodes.append(Node(**node_data))
                    # Insertar los nuevos nodos propuestos
                    updated_nodes.extend(new_nodes)
                    continue
                elif in_target_section:
                    # Finalizó la sección objetivo
                    in_target_section = False

            if not in_target_section:
                updated_nodes.append(Node(**node_data))

        if not section_found:
            # Si la sección no existía, la agregamos al final con su encabezado
            updated_nodes.append(
                Node(
                    type="heading",
                    attrs={"level": 2},
                    content=[Node(type="text", text=section_title)],
                )
            )
            updated_nodes.extend(new_nodes)

        return DocumentContent(type="doc", content=updated_nodes)

    @classmethod
    def _to_response(cls, gen: GenerationModel) -> GenerationResponse:
        return GenerationResponse(
            generation_id=gen.id,
            document_id=gen.document_id,
            section_id=gen.section_id,
            section_title=gen.section_title,
            status=gen.status,
            content=gen.content,
            original_section_content=gen.original_section_content,
            metadata_info={
                "provider": gen.provider,
                "model": gen.model,
                "prompt_version": gen.prompt_version,
                "latency_ms": gen.latency_ms,
                "tokens_used": gen.tokens_used,
                "error_message": gen.error_message,
            },
            created_at=gen.created_at,
        )
