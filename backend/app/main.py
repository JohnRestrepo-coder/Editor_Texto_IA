from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.modules.ai_generation.router import router as generation_router
from backend.app.modules.document_mgmt.router import router as document_router
from backend.app.modules.export_engine.router import router as export_router
from backend.app.modules.template_mgmt.router import router as template_router

# Inicialización directa de la base de datos
init_db()

app = FastAPI(
    title="AI Document Studio API",
    version="1.0.0",
    description="Backend modular para creación, edición estructurada y exportación con IA.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(document_router, prefix=settings.API_V1_PREFIX)
app.include_router(template_router, prefix=settings.API_V1_PREFIX)
app.include_router(generation_router, prefix=settings.API_V1_PREFIX)
app.include_router(export_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "AI Document Studio API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }
