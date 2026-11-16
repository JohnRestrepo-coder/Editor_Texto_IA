# AGENTS.md — AI Document Studio

## Misión
Construir AI Document Studio de acuerdo con las especificaciones aprobadas y la Constitution del proyecto.

## Orden de precedencia
1. Instrucciones explícitas más recientes del propietario del proyecto.
2. Constitution aprobada.
3. Especificaciones aprobadas en `specs/`.
4. Contratos versionados en `docs/contracts/` y dentro de cada especificación.
5. Planes y tareas aprobados.
6. Este archivo y convenciones locales.

Si dos fuentes del mismo nivel se contradicen, no elijas arbitrariamente: documenta el conflicto y solicita aclaración.

## Antes de trabajar
- Inspecciona el estado de Git y los cambios no confirmados.
- Lee la especificación y contratos de la tarea.
- Identifica dependencias y archivos bajo tu ownership.
- No sobrescribas archivos existentes sin inspeccionarlos.
- Confirma criterios de aceptación y pruebas esperadas.

## Reglas de implementación
- No implementar requisitos no especificados.
- No cambiar contratos compartidos unilateralmente.
- No introducir dependencias sin justificar su necesidad.
- No agregar microservicios, colas, vector DB o frameworks adicionales por moda.
- No exponer claves ni secretos.
- Mantener las dependencias de infraestructura detrás de interfaces cuando corresponda.
- Validar todas las entradas y salidas externas.
- Mantener compatibilidad con contratos publicados o versionar cambios incompatibles.

## Ownership sugerido
- Product/Analyst: requisitos, historias y criterios de aceptación.
- Architect: arquitectura, contratos y ADR.
- Frontend: `frontend/`.
- Backend: `backend/`.
- AI: módulo `backend/app/modules/ai_generation/` y `prompts/`.
- QA: pruebas, estrategia de calidad y reportes.
El ownership definitivo se ajustará a la estructura real del repositorio.

## Trabajo paralelo
- No permitir que dos agentes editen el mismo archivo simultáneamente.
- Asignar tareas con límites de carpetas claros.
- Usar ramas o worktrees si están disponibles.
- Los contratos compartidos requieren revisión del arquitecto y aprobación del propietario.

## Definition of Done
Una tarea está terminada solo cuando:
1. Cumple los criterios de aceptación.
2. Tiene pruebas adecuadas.
3. Las pruebas se ejecutaron y se reportó el resultado.
4. No introduce secretos ni archivos temporales innecesarios.
5. La documentación y contratos están actualizados.
6. Se informa qué cambió, qué no se hizo y qué riesgos quedan.

## Formato del informe de agente
- Objetivo de la tarea.
- Especificación y criterios relacionados.
- Archivos creados/modificados.
- Decisiones tomadas y justificación.
- Pruebas ejecutadas y resultado.
- Limitaciones y riesgos.
- Preguntas que requieren aprobación.
