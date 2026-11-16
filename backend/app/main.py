from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.modules.document_mgmt.router import router as document_router

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


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "AI Document Studio API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }
