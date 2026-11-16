import logging
import time
from abc import ABC, abstractmethod
from typing import Any, ClassVar

import httpx
from pydantic import BaseModel, Field

from backend.app.config import settings
from backend.app.modules.ai_generation.prompts import PromptManager

logger = logging.getLogger(__name__)


class LLMRequest(BaseModel):
    prompt: str
    system_instruction: str = ""
    context: dict[str, Any] = Field(default_factory=dict)
    max_tokens: int = 2000
    temperature: float = 0.7


class LLMResponse(BaseModel):
    content_json: dict[str, Any]
    raw_text: str
    model: str
    provider: str
    prompt_version: str = "v2"
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
                            "text": f"Contenido generado para la sección '{section_title}'. Se han considerado las directrices y el tono del documento.",
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
            prompt_version="v2",
            latency_ms=max(1, latency_ms),
            tokens_used=180,
        )


class GeminiLLMProvider(LLMProvider):
    """
    Adaptador para Google Gemini API utilizando llamadas HTTP estándar y salida estructurada JSON.
    Usa autenticación por encabezado x-goog-api-key y soporte para modelos modernos.
    """

    CANDIDATE_MODELS: ClassVar[list[str]] = [
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-1.5-flash",
    ]

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-3.5-flash-lite"
        self.mock_fallback = MockLLMProvider()

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY no configurada. Utilizando MockLLMProvider para pruebas locales."
            )
            response = self.mock_fallback.generate(request)
            response.provider = "mock-no-api-key"
            response.model = self.model
            return response

        start_time = time.time()
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        payload: dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": request.prompt}],
                }
            ],
            "generationConfig": {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
            },
        }

        if request.system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": request.system_instruction}]
            }

        models_to_try = [self.model] + [
            m for m in self.CANDIDATE_MODELS if m != self.model
        ]
        last_error: Exception | None = None

        for target_model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent"
            try:
                with httpx.Client(timeout=45.0) as client:
                    res = client.post(url, headers=headers, json=payload)

                    if res.status_code == 404:
                        logger.warning(
                            f"Modelo '{target_model}' no disponible (404). Intentando siguiente modelo..."
                        )
                        continue

                    if res.status_code != 200:
                        raise RuntimeError(
                            f"Error de la API de Google Gemini (HTTP {res.status_code}): {res.text[:300]}"
                        )

                    data = res.json()

                latency_ms = int((time.time() - start_time) * 1000)
                candidates = data.get("candidates", [])
                if not candidates:
                    raise ValueError(
                        "La API de Gemini no devolvió candidatos válidos en la respuesta."
                    )

                parts = candidates[0].get("content", {}).get("parts", [])
                raw_text = parts[0].get("text", "") if parts else ""
                parsed_json = PromptManager.parse_llm_json(raw_text)

                usage = data.get("usageMetadata", {})
                tokens_used = usage.get("totalTokenCount", 0)

                return LLMResponse(
                    content_json=parsed_json,
                    raw_text=raw_text,
                    model=target_model,
                    provider="gemini",
                    prompt_version="v2",
                    latency_ms=latency_ms,
                    tokens_used=tokens_used,
                )

            except (
                httpx.HTTPError,
                ValueError,
                KeyError,
                RuntimeError,
                TimeoutError,
            ) as e:
                logger.error(f"Fallo al invocar modelo '{target_model}': {e!s}")
                last_error = e

        # Si llegamos aquí con api_key configurada, propagamos el error real para no fingir respuestas
        raise RuntimeError(
            f"No fue posible generar contenido con Google Gemini: {last_error}"
        )


def get_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER.lower() == "gemini":
        return GeminiLLMProvider()
    return MockLLMProvider()
