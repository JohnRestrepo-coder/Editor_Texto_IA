# Feature Specification: Generación con IA

**Feature Branch**: `003-ai-generation`
**Estado**: Borrador para revisión
**Prioridad**: P1

## User Scenarios & Testing

### US-001 — Generar una sección
Como usuario, quiero generar una sección con IA utilizando instrucciones, fuentes y contexto pertinente.

### US-002 — Revisar y aceptar propuesta
Como usuario, quiero revisar el resultado antes de aplicarlo al documento.

### US-003 — Rechazar o regenerar
Como usuario, quiero descartar una propuesta o pedir otra sin perder el contenido original.

### US-004 — Generar documento completo
Como usuario, quiero solicitar la generación de todas las secciones habilitadas, siguiendo el orden y dependencias definidos por la plantilla.

## Functional Requirements
- FR-001: El sistema MUST generar contenido principalmente por sección.
- FR-002: La solicitud MUST identificar documento y sección.
- FR-003: El motor MUST reunir contexto global, de plantilla, fuentes y secciones relacionadas.
- FR-004: El motor MUST recuperar solo el contexto pertinente, evitando enviar todo el material innecesariamente.
- FR-005: Los prompts MUST estar versionados.
- FR-006: El PMV MUST integrar un único proveedor mediante interfaz/adaptador.
- FR-007: Las salidas MUST cumplir un esquema estructurado.
- FR-008: El backend MUST validar la salida estructural y reglas de negocio.
- FR-009: La generación MUST producir una propuesta separada del documento persistido.
- FR-010: El usuario MUST aceptar explícitamente antes de aplicar la propuesta.
- FR-011: Rechazar una propuesta MUST conservar el contenido original.
- FR-012: Regenerar una sección MUST NOT modificar otras secciones.
- FR-013: La generación completa MUST coordinar secciones en orden topológico respetando dependencias.
- FR-014: Registrar proveedor, modelo, versión de prompt, fecha, uso de tokens/costo si existe, latencia, estado y error.
- FR-015: El contenido de las fuentes MUST tratarse como datos no confiables y no como instrucciones de sistema.

## Output requirements
La respuesta del modelo será un objeto estructurado que contiene bloques documentales compatibles con el modelo aprobado. No insertar HTML arbitrario ni aceptar contenido sin validación.

## Out of Scope
- Selección de múltiples proveedores por usuario en UI.
- Agentes autónomos con herramientas externas.
- RAG/vector database obligatorio en el PMV.
- Generación desatendida que aplique cambios automáticamente.

## Acceptance Criteria
- Generar una sección y mostrar vista previa.
- Aceptar aplica solo esa propuesta a la sección correspondiente.
- Rechazar no altera el documento.
- Regenerar no altera otras secciones.
- Errores del proveedor y salidas inválidas se gestionan de forma segura.
- Cada generación tiene registro de trazabilidad.
