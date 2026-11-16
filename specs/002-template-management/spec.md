# Feature Specification: Gestión de plantillas

**Feature Branch**: `002-template-management`
**Estado**: Borrador para revisión
**Prioridad**: P1

## User Scenarios & Testing

### US-001 — Crear plantilla nativa
Como usuario, quiero definir una plantilla con nombre, instrucciones, secciones y estilos para reutilizar una estructura documental.

### US-002 — Crear documento desde plantilla
Como usuario, quiero seleccionar una plantilla y abrir el editor común con las secciones precargadas.

### US-003 — Importar DOCX existente
Como usuario, quiero cargar un Word existente y configurarlo como plantilla sin perder el archivo original.

## Functional Requirements
- FR-001: El sistema MUST permitir crear, consultar, actualizar y archivar plantillas nativas.
- FR-002: Una plantilla MUST contener metadatos, secciones ordenadas, instrucciones y perfil de estilos.
- FR-003: El sistema MUST permitir crear un documento a partir de una plantilla.
- FR-004: El sistema MUST permitir cargar un DOCX existente.
- FR-005: La importación MUST conservar el archivo original.
- FR-006: La importación MUST producir un análisis preliminar de estructura/estilos y permitir mapeo humano.
- FR-007: Las secciones podrán declarar dependencias para la generación.
- FR-008: Las plantillas deberán distinguir `native` y `docx`.
- FR-009: La aplicación MUST utilizar el mismo editor para ambos orígenes.

## Import DOCX behavior
No se asumirá que cualquier DOCX puede convertirse automáticamente en una plantilla editable perfecta. El sistema debe detectar lo que pueda, presentar el resultado y permitir al usuario configurar secciones y marcadores. Elementos no soportados deben señalarse.

## Out of Scope
- Conversión automática perfecta de cualquier documento Word.
- Marketplace público de plantillas.
- Edición colaborativa.

## Acceptance Criteria
- Crear plantilla nativa con secciones ordenadas.
- Crear documento desde plantilla en el editor común.
- Cargar DOCX, conservar original y mostrar análisis/mapeo configurable.
- Validar archivos y rechazar formatos no admitidos.
