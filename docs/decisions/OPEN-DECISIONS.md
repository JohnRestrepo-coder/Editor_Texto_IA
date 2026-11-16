# Decisiones de AI Document Studio

## Decisiones Resueltas (Aprobadas 2026-11-16)

1. **Proveedor y modelo IA inicial:** Gemini API (con modelo gratuito/de bajo costo como Gemini 1.5/2.5 Flash o Gemini Pro), bajo una interfaz `LLMProvider` extensible a DeepSeek u otros proveedores gratuitos.
2. **Autenticación/Acceso:** Monousuario para el PMV (acceso directo sin login para evaluar funcionalidad de inmediato).
3. **Persistencia para desarrollo:** SQLite con SQLAlchemy (asíncrono con aiosqlite), manteniendo portabilidad a PostgreSQL para producción.
4. **Almacenamiento de archivos:** Local (`storage/`) para el PMV, con validaciones estrictas de tamaño y path traversal.
5. **Motor de exportación a PDF:** Aprobado Playwright / Chromium headless.

## Decisiones Pendientes (Para Fases 2, 3 y 4)

1. Límites de tamaño, tipos MIME y número de archivos cargados para fuentes (Fase 2).
2. DOCX institucionales de referencia para pruebas de compatibilidad y fidelidad (Fase 2 / Fase 4).
3. Parámetros de timeout, reintentos y temperatura para el adaptador de Gemini (Fase 3).
4. Ejecución de generación completa: Síncrona vs. asíncrona con SSE (Fase 3).
5. Estrategia de empaquetado para despliegue final (Docker Compose o binario local).
