# Implementation Plan: Exportación documental

## Diseño
Crear una frontera `DocumentExporter` con implementaciones independientes para DOCX nativo, DOCX basado en plantilla y PDF.

## DOCX
- Evaluar python-docx para documentos nativos.
- Evaluar docxtpl + python-docx para rellenar DOCX existentes.
- Mantener una matriz de nodos/estilos soportados.
- Conservar el DOCX original y producir un archivo nuevo.
- Validar que el archivo ZIP/DOCX sea legible y que el contenido esperado exista.

## PDF
- Renderizar una vista de impresión HTML/CSS.
- Evaluar Playwright/Chromium para generar PDF.
- Asegurar que el CSS de impresión tenga reglas explícitas de página y saltos.

## Riesgos
- WordprocessingML tiene capacidades que no tienen equivalencia directa en Tiptap.
- Numeración, secciones, encabezados/pies y tablas complejas pueden perder fidelidad.
- Diferencias entre motores de renderizado.

## Pruebas
- Documentos patrón con formato simple y complejo.
- Verificación estructural del DOCX.
- Render PDF y revisión visual.
- Pruebas de contenido y caracteres especiales.

## Pendientes
- Aprobar biblioteca DOCX definitiva.
- Crear/seleccionar archivos patrón institucionales.
- Definir métricas de fidelidad aceptables.
