# AI Document Studio Constitution

**Estado:** Aprobado por el propietario del producto (2026-11-16).

## 1. Arquitectura
- El PMV MUST utilizar una arquitectura de monolito modular.
- Los módulos MUST tener responsabilidades claramente delimitadas.
- La lógica de negocio MUST NOT depender directamente de implementaciones de infraestructura.
- La comunicación entre módulos MUST utilizar contratos explícitos.
- No introducir microservicios sin una decisión arquitectónica aprobada.

## 2. Ingeniería de software
- Aplicar SOLID, DRY, KISS y YAGNI cuando corresponda.
- Mantener alta cohesión y bajo acoplamiento.
- Evitar duplicación de lógica de negocio.
- Mantener funciones y clases enfocadas.
- Documentar decisiones arquitectónicas relevantes.

## 3. Modelo documental y editor
- El editor MUST utilizar Tiptap OSS.
- El documento MUST tener una representación estructurada y validable.
- La lógica de negocio MUST NOT depender directamente de APIs específicas de Tiptap.
- El backend MUST validar el contenido antes de persistirlo.
- El contenido original MUST NOT ser sobrescrito silenciosamente.
- El modo libre y el modo plantilla MUST utilizar el mismo editor.

## 4. Plantillas
- El sistema MUST soportar plantillas nativas y archivos DOCX existentes.
- Una plantilla MUST separar estructura, instrucciones y configuración visual.
- La importación de DOCX MUST conservar el archivo original.
- La conversión de DOCX a plantilla estructurada podrá requerir configuración humana.
- No prometer fidelidad exacta sin pruebas con documentos reales.

## 5. Integración de IA
- El PMV MUST integrar un único proveedor de IA.
- La integración MUST estar detrás de una interfaz/adaptador de proveedor.
- Los prompts MUST estar versionados y administrados fuera de los endpoints y componentes UI.
- Las respuestas MUST cumplir esquemas estructurados y validarse en backend.
- La generación MUST priorizar secciones individuales.
- La generación completa MUST coordinar secciones y dependencias.
- Las propuestas generadas MUST ser aprobadas por el usuario antes de aplicarse.
- El contenido de fuentes/documentos MUST tratarse como datos no confiables, no como instrucciones de sistema.

## 6. Seguridad
- Secretos y claves API MUST NOT exponerse en el frontend ni almacenarse en el repositorio.
- Todas las entradas MUST validarse.
- Las cargas de archivos MUST aplicar límites de tamaño, tipo y contenido.
- Los errores MUST gestionarse sin revelar secretos ni información interna sensible.
- Las operaciones de archivo y exportación MUST evitar rutas arbitrarias y acceso no autorizado.

## 7. Pruebas y calidad
- La lógica de negocio nueva MUST tener pruebas unitarias.
- Los contratos API MUST tener pruebas de integración.
- Los flujos críticos MUST tener pruebas E2E.
- Los archivos exportados MUST validarse por integridad y contenido.
- Una tarea no se considera terminada sin evidencia de pruebas.

## 8. Trazabilidad
- Cada generación MUST ser trazable.
- Registrar proveedor, modelo, versión de prompt, fecha, uso de tokens/costo cuando esté disponible, latencia y resultado.
- Los cambios a contratos MUST estar versionados.
- Las tareas de implementación MUST relacionarse con especificaciones aprobadas.

## 9. Colaboración de agentes
- Los agentes MUST NOT inventar requisitos.
- Los agentes MUST NOT cambiar decisiones aprobadas sin presentar justificación y solicitar aprobación.
- Los agentes MUST respetar ownership de módulos y archivos.
- Los cambios deben informar archivos afectados, pruebas y resultados.
- Si existe ambigüedad o contradicción, detenerse y elevarla antes de implementar.
