# ADR-001: Arquitectura inicial de AI Document Studio

- Estado: Aprobado por el propietario del producto
- Fecha: 2026-11-16

## Contexto
El producto necesita editor enriquecido, plantillas, generación con IA, gestión de fuentes y exportación DOCX/PDF. El PMV debe ser mantenible y permitir evolución sin complejidad operativa innecesaria.

## Decisiones Aprobadas
- **Arquitectura:** Monolito modular.
- **Frontend:** React + TypeScript + Vite.
- **Editor:** Tiptap OSS desacoplado de la lógica de dominio.
- **Backend:** Python + FastAPI.
- **Validación:** Pydantic v2 con esquemas JSON versionados.
- **Persistencia PMV:** SQLite local mediante SQLAlchemy async, manteniendo portabilidad a PostgreSQL para producción.
- **Modo de acceso:** Monousuario para el PMV (acceso directo a la interfaz sin barrera de autenticación).
- **Almacenamiento:** Almacenamiento local en sistema de archivos (`storage/`).
- **Proveedor LLM:** Gemini API (capa gratuita de Gemini Pro / Flash) a través de una interfaz abstracta `LLMProvider` que permita incorporar DeepSeek u otros proveedores sin costo.
- **Generación:** Generación por sección como flujo prioritario, con propuestas en borrador sujetas a aprobación explícita.
- **Exportación DOCX:** Adaptadores para `python-docx` (nativo) y `docxtpl` (relleno de plantillas importadas).
- **Exportación PDF:** HTML/CSS de impresión + Playwright/Chromium headless.

## Consecuencias
- Despliegue y ejecución local inmediata sin requerir servicios externos activos para iniciar.
- Simplicidad operativa y costo cero en la etapa inicial de validación.
- Los límites de módulos y contratos se mantienen de forma estricta para garantizar escalabilidad hacia PostgreSQL y multiusuario futuro.
