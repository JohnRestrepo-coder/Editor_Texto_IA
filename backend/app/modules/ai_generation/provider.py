import time
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import BaseModel, Field

from backend.app.config import settings
from backend.app.modules.ai_generation.prompts import PromptManager


class LLMRequest(BaseModel):
    prompt: str
    system_instruction: str = ""
    context: dict[str, Any] = Field(default_factory=dict)
    max_tokens: int = 1500
    temperature: float = 0.7


class LLMResponse(BaseModel):
    content_json: dict[str, Any]
    raw_text: str
    model: str
    provider: str
    prompt_version: str = "v1"
    latency_ms: int = 0
    tokens_used: int | None = None


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Genera una respuesta estructurada a partir del prompt."""


class MockLLMProvider(LLMProvider):
    """
    Proveedor simulado para pruebas unitarias, desarrollo local sin costo y entornos offline.
    Genera contenido estructurado Tiptap coherente con la sección solicitada.
    """

    def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()

        section_title = request.context.get("section_title", "Sección")
        instructions = request.context.get("guidelines", "")

        mock_content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Este es el contenido generado asistido por IA para la sección '{section_title}'. Se han considerado las directrices y el tono del documento.",
                        }
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Pautas aplicadas: {instructions or 'Redacción ejecutiva clara, concisa y orientada a resultados.'}",
                        }
                    ],
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Punto clave 1: Definición clara de objetivos y alcance.",
                                        }
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Punto clave 2: Métricas de éxito y seguimiento de avance.",
                                        }
                                    ],
                                }
                            ],
                        },
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "En conclusión, los puntos expuestos garantizan la consistencia estructural requerida para este apartado.",
                        }
                    ],
                },
            ],
        }

        latency_ms = int((time.time() - start_time) * 1000)

        return LLMResponse(
            content_json=mock_content,
            raw_text="mock_generated_json",
            model="mock-v1",
            provider="mock",
            prompt_version="v1",
            latency_ms=max(1, latency_ms),
            tokens_used=180,
        )


class GeminiLLMProvider(LLMProvider):
    """
    Adaptador para Google Gemini API utilizando llamadas HTTP estándar y salida estructurada JSON.
    Si la API key no está configurada, recurre transparentemente al proveedor simulado.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-1.5-flash"
        self.mock_fallback = MockLLMProvider()

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            # Fallback seguro para entorno de desarrollo / sin costo
            response = self.mock_fallback.generate(request)
            response.provider = "gemini-mock-fallback"
            response.model = self.model
            return response

        start_time = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": request.system_instruction}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": request.prompt}],
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
            },
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()

            latency_ms = int((time.time() - start_time) * 1000)

            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("La API de Gemini no devolvió candidatos válidos.")

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            parsed_json = PromptManager.parse_llm_json(raw_text)

            usage = data.get("usageMetadata", {})
            tokens_used = usage.get("totalTokenCount", 0)

            return LLMResponse(
                content_json=parsed_json,
                raw_text=raw_text,
                model=self.model,
                provider="gemini",
                prompt_version="v1",
                latency_ms=latency_ms,
                tokens_used=tokens_used,
            )
        except (httpx.HTTPError, ValueError, KeyError):
            # En caso de error de red o cuota en desarrollo, retornar fallback con metadatos de error
            fallback = self.mock_fallback.generate(request)
            fallback.provider = "gemini-error-fallback"
            fallback.model = self.model
            return fallback


def get_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER.lower() == "gemini":
        return GeminiLLMProvider()
    return MockLLMProvider()
