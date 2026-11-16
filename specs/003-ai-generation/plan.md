# Implementation Plan: Generación con IA

## Componentes
- `AI Generation`: orquestación de casos de uso.
- `Context Manager`: recuperación de contexto pertinente.
- `Prompt Manager`: carga y versionado de prompts.
- `LLMProvider`: interfaz independiente del SDK.
- Adaptador del único proveedor inicial.
- `Output Validator`: validación de esquema y reglas.
- `Generation Repository`: persistencia de propuestas y metadatos.

## Contrato conceptual del proveedor
`generate(request: LLMRequest) -> LLMResponse` como operación asíncrona. El contrato final debe modelarse con Pydantic y documentarse.

## Flujo
1. Validar documento, sección y permisos.
2. Recuperar contexto relevante y fuentes.
3. Cargar versión aprobada del prompt.
4. Llamar al adaptador del proveedor.
5. Validar salida estructurada y reglas de negocio.
6. Persistir generación como propuesta.
7. Presentar vista previa.
8. Aceptar/rechazar explícitamente.
9. Al aceptar, verificar versión del documento y actualizar solo la sección objetivo.

## Riesgos
- Prompt injection en fuentes.
- Alucinaciones o afirmaciones no respaldadas.
- Límites de contexto, costo y latencia.
- Incompatibilidades de JSON Schema entre proveedores.
- Conflictos si el documento cambia mientras se genera.

## Pruebas
- Proveedor simulado para pruebas deterministas.
- Salidas válidas, malformadas e incompletas.
- Fallos, timeout y rate limit.
- Aceptación/rechazo.
- Regeneración aislada de sección.
- Conflicto de versión del documento.
- Pruebas de seguridad para contenido fuente malicioso.

## Pendientes
- Seleccionar proveedor/modelo.
- Definir límites de tokens, timeout y reintentos.
- Definir política de costo y retención de prompts/respuestas.
