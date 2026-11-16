# AI Document Studio — paquete inicial Spec Kit

Este paquete contiene la base inicial de especificaciones y contratos para iniciar el proyecto con Antigravity y Spec Kit.

## Instrucciones de uso

1. Copia el contenido de esta carpeta en la raíz del repositorio de AI Document Studio.
2. Revisa primero `ANTIGRAVITY_BRIEF.txt`.
3. Revisa y aprueba `.specify/memory/constitution.md`.
4. Ejecuta el flujo de Spec Kit disponible en tu instalación. No asumas nombres de comandos: verifica los comandos de la versión instalada.
5. Usa las especificaciones numeradas como fuente de verdad. No implementes funcionalidades sin revisar `spec.md`, `plan.md`, `tasks.md` y los contratos correspondientes.
6. Completa las decisiones marcadas como `PENDIENTE` antes de implementar los módulos que dependan de ellas.

## Estado

Estos documentos son una propuesta inicial de diseño. No son prueba de que el código exista ni de que las tecnologías estén instaladas. Los campos y endpoints son contratos iniciales que deben validarse y versionarse.

## Decisiones confirmadas por el usuario

- Editor: Tiptap OSS.
- Plantillas Word: ambos escenarios, creación desde cero y carga/relleno de DOCX existentes.
- Proveedores IA: integrar uno inicialmente, conservando una abstracción para futuros proveedores.
- Generación: priorizar por sección. La generación completa coordina las secciones.
- Arquitectura: monolito modular para el PMV.

## Decisiones pendientes

- Proveedor/modelo de IA inicial.
- Versiones concretas de dependencias.
- Política de autenticación y autorización según despliegue.
- Almacenamiento de archivos para producción.
- Límites máximos de tamaño y formatos de carga.
- Estrategia definitiva de exportación DOCX para documentos nativos.
- Reglas de fidelidad y documentos patrón para pruebas de exportación.
