# Feature Specification: Exportación documental

**Feature Branch**: `004-document-export`
**Estado**: Borrador para revisión
**Prioridad**: P1

## User Scenarios & Testing

### US-001 — Exportar DOCX desde documento nativo
Como usuario, quiero descargar un documento creado en el editor como archivo Word.

### US-002 — Rellenar plantilla DOCX existente
Como usuario, quiero exportar un documento basado en un DOCX institucional conservando el formato original en la medida soportada.

### US-003 — Exportar PDF
Como usuario, quiero descargar una versión PDF del documento.

## Functional Requirements
- FR-001: El sistema MUST exportar DOCX desde el modelo documental.
- FR-002: El sistema MUST soportar exportación utilizando una plantilla DOCX importada.
- FR-003: El exportador MUST mapear solo nodos y marcas soportados.
- FR-004: Elementos no soportados MUST reportarse; no descartarse silenciosamente.
- FR-005: El sistema MUST permitir exportar PDF.
- FR-006: El archivo exportado MUST validarse por integridad antes de entregarse.
- FR-007: El exportador MUST ser independiente de la lógica de negocio y del editor.
- FR-008: El archivo original de plantilla MUST permanecer sin cambios.
- FR-009: Los errores de exportación MUST ser comprensibles y trazables.

## DOCX quality
No se garantiza fidelidad pixel-perfect. Deben existir documentos de referencia para comprobar estilos, márgenes, tablas, listas, encabezados, pies, imágenes, numeración y saltos de página.

## PDF quality
Probar paginación, fuentes, márgenes, encabezados, pies, tablas y cortes de contenido.

## Out of Scope
- Exportación RTF.
- Edición avanzada de WordprocessingML.
- Garantía de equivalencia exacta entre Word, LibreOffice y render PDF.

## Acceptance Criteria
- DOCX descargable y válido desde documento nativo.
- DOCX basado en plantilla importada conserva los elementos del documento patrón dentro del alcance probado.
- PDF descargable y legible.
- Elementos no soportados se reportan.
- Pruebas automatizadas de integridad y pruebas visuales con documentos patrón.
