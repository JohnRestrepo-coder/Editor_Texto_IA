# AI Document Studio (Editor_Texto_IA)

AI Document Studio es un editor de texto enriquecido tipo Word con asistencia de inteligencia artificial integrada para redactar, estructurar y exportar documentos de forma asistida y controlada.

## 🚀 Características Principales

- **Editor Enriquecido Unificado:** Basado en Tiptap OSS, soporta párrafos, encabezados, negrita, cursiva, subrayado, listas, citas y tablas.
- **Modo Libre y Modo Plantilla:** Un único editor para documentos desde cero o basados en plantillas.
- **Control de Versión Optimista:** Prevención de sobrescritura silenciosa ante ediciones simultáneas (`expected_version`).
- **Arquitectura Monolítica Modular:** Backend desacoplado en FastAPI con SQLite/SQLAlchemy y frontend React + TypeScript + Vite.
- **Especificaciones Formales con Spec Kit:** Gobernanza bajo SDD (Spec-Driven Development), constitution aprobada y contratos versionados.

## 📁 Estructura del Proyecto

```text
├── .specify/             # Gobernanza y constitution de Spec Kit 1.2.2
├── docs/                 # Contratos OpenAPI y decisiones arquitectónicas (ADRs)
├── specs/                # Especificaciones formales por feature (001 a 004)
├── backend/              # API modular FastAPI + Pydantic v2 + SQLAlchemy
│   ├── app/              # Configuración, base de datos y módulos de dominio
│   └── tests/            # Suite de pruebas unitarias y de esquema
├── frontend/             # SPA React 18/19 + TypeScript + Vite + Tailwind + Tiptap
│   └── src/              # Componentes del editor, toolbar y sidebar
└── storage/              # Almacenamiento local protegido para desarrollo
```

## 🛠️ Instrucciones de Ejecución Local

### 1. Backend (FastAPI)
```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Ejecutar el servidor backend
uvicorn backend.app.main:app --reload --port 8000
```
La API estará disponible en `http://127.0.0.1:8000` con documentación interactiva Swagger en `/docs`.

### 2. Frontend (React + Vite)
```bash
cd frontend
npm run dev
```
La aplicación web estará disponible en `http://localhost:5173`.

### 3. Ejecutar Pruebas
```bash
.\.venv\Scripts\pytest -v backend/tests
```

## 📄 Licencia
Este proyecto se distribuye bajo la licencia especificada en [LICENSE](LICENSE).
