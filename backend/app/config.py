from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./storage/ai_document_studio.db"
    STORAGE_DIR: str = "./storage"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure local storage directories exist
os.makedirs(os.path.join(settings.STORAGE_DIR, "uploads"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "templates"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "exports"), exist_ok=True)
