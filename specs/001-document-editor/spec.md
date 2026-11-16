# Feature Specification: Editor documental

**Feature Branch**: `001-document-editor`
**Estado**: Borrador para revisión
**Prioridad**: P0 — base del producto

## User Scenarios & Testing

### US-001 — Crear documento libre (P1)
Como usuario, quiero crear un documento en blanco para empezar a escribir sin seleccionar una plantilla.

**Acceptance scenarios**
1. Given que estoy en la pantalla inicial, When selecciono “Editor libre”, Then se abre el editor con un documento vacío.
2. Given un documento nuevo, When ingreso contenido y guardo, Then el documento queda persistido y puede recuperarse.
3. Given un documento guardado, When vuelvo a abrirlo, Then se restaura su contenido.

### US-002 — Editar contenido enriquecido (P1)
Como usuario, quiero aplicar formato a mi contenido.

**Acceptance scenarios**
1. El editor permite párrafos, encabezados, negrita, cursiva, subrayado y listas.
2. Las tablas y enlaces se soportan de acuerdo con el alcance implementado.
3. El contenido guardado conserva la estructura y formato soportados.

### US-003 — Guardado seguro (P1)
Como usuario, quiero que mis cambios se guarden sin perder versiones por sobrescrituras concurrentes.

**Acceptance scenarios**
1. El backend valida el contenido recibido.
2. El guardado usa control de versión optimista o mecanismo equivalente.
3. Si existe conflicto de versión, el sistema informa el conflicto y no sobrescribe silenciosamente.

## Functional Requirements
- FR-001: El sistema MUST permitir crear documentos libres.
- FR-002: El sistema MUST utilizar el mismo editor para documentos libres y basados en plantillas.
- FR-003: El editor MUST utilizar Tiptap OSS.
- FR-004: El contenido MUST almacenarse como estructura JSON validada, no exclusivamente HTML.
- FR-005: El sistema MUST soportar el conjunto de nodos y marcas definido en el contrato documental.
- FR-006: El usuario MUST poder guardar y recuperar documentos.
- FR-007: El backend MUST validar estructura, tamaño y versión del contenido.
- FR-008: El guardado MUST detectar conflictos de concurrencia.
- FR-009: El sistema MUST preservar el contenido no modificado durante actualizaciones parciales cuando estas se implementen.

## Non-Functional Requirements
- NFR-001: La lógica de dominio no dependerá directamente de Tiptap.
- NFR-002: Los errores de persistencia serán explícitos y no causarán pérdida silenciosa.
- NFR-003: Las operaciones críticas tendrán pruebas unitarias e integración.
- NFR-004: No almacenar secretos en frontend.

## Out of Scope
- Colaboración multiusuario en tiempo real.
- Historial avanzado de revisiones tipo control de cambios.
- Exportación final DOCX/PDF (feature 004).
- Generación IA (feature 003).

## Dependencies
- Contrato documental compartido.
- Persistencia configurada.
- Aplicación frontend/backend inicial.

## Acceptance Criteria
- Un usuario puede crear, editar, guardar, cerrar y recuperar un documento.
- Los formatos incluidos en el alcance se conservan tras guardar y volver a abrir.
- Un conflicto de versión se detecta y no destruye cambios existentes.
