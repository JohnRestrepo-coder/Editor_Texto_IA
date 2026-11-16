# Implementation Plan: Editor documental

## Propuesta técnica
- React + TypeScript en frontend.
- Tiptap OSS encapsulado en un componente/adaptador de editor.
- Backend FastAPI.
- Modelo de dominio de documento y validación Pydantic.
- Persistencia relacional propuesta con PostgreSQL/SQLAlchemy.
- API REST versionada `/api/v1`.

## Límites
El frontend gestiona interacción y estado visual. El backend valida y persiste. La lógica de dominio no debe importar componentes ni extensiones de Tiptap.

## Riesgos
- Desfase entre JSON generado por Tiptap y esquema permitido por backend.
- Conflictos de guardado.
- Extensiones de editor que no tengan representación en exportación.

## Plan de pruebas
- Unitarias para validación del modelo documental.
- Integración para crear/actualizar/recuperar documentos.
- E2E para flujo libre y recuperación.
- Pruebas de round-trip JSON editor -> API -> persistencia -> editor.

## Pendientes
- Confirmar autenticación y modelo de usuarios.
- Definir tamaño máximo de documento.
- Definir conjunto final de extensiones Tiptap y versiones.
