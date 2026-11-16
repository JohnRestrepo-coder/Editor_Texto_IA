import { test, expect } from '@playwright/test';

test.describe('Feature 001 & 002: Editor Documental y Gestión de Plantillas E2E', () => {
  test('debe cargar la aplicación y mostrar el editor Tiptap con documento inicial', async ({ page }) => {
    await page.goto('/');

    // Verificar que la cabecera del editor y la barra lateral estén presentes
    await expect(page.locator('text=Document Studio')).toBeVisible();
    await expect(page.locator('button:has-text("Editor Libre")')).toBeVisible();
    await expect(page.locator('button:has-text("Usar Plantilla / DOCX")')).toBeVisible();

    // El editor enriquecido debe estar presente y enfocado
    const editor = page.locator('.ProseMirror');
    await expect(editor).toBeVisible();

    // Debe mostrar la versión inicial v1
    await expect(page.locator('header').locator('text=v1')).toBeVisible();
  });

  test('debe permitir crear un nuevo documento en blanco, escribir y guardar', async ({ page }) => {
    await page.goto('/');

    // Crear un nuevo documento libre desde la barra lateral
    await page.click('button:has-text("Editor Libre")');

    // Cambiar el título del documento
    const titleInput = page.locator('input[placeholder="Título del documento..."]');
    await titleInput.fill('Reporte Técnico Automatizado E2E');

    // Escribir en el editor Tiptap
    const editor = page.locator('.ProseMirror');
    await editor.click();
    await editor.fill('Este es el contenido inicial redactado en la prueba E2E.');

    // Aplicar formato de encabezado con la barra de herramientas
    await page.click('button[title="Encabezado 1"]');

    // Guardar los cambios
    await page.click('button:has-text("Guardar")');

    // Esperar a que el estado cambie a "Guardado" y la versión incremente a v2
    await expect(page.locator('text=Guardado')).toBeVisible();
    await expect(page.locator('header').locator('text=v2')).toBeVisible();

    // Verificar que en la barra lateral aparezca el título actualizado
    await expect(page.locator('aside').locator('text=Reporte Técnico Automatizado E2E')).toBeVisible();
  });

  test('debe abrir modal de plantillas, crear documento desde plantilla y cargarlo en el mismo editor', async ({ page }) => {
    await page.goto('/');

    // Abrir el modal de plantillas desde la barra lateral
    await page.click('button:has-text("Usar Plantilla / DOCX")');

    // Verificar que el modal abra
    await expect(page.locator('text=Gestor de Plantillas e Importación DOCX')).toBeVisible();

    // Ir a pestaña de diseñar plantilla nativa
    await page.click('button:has-text("Diseñar Plantilla Nativa")');

    // Llenar datos de la plantilla
    await page.fill('input[placeholder="Ej. Plan de Trabajo Trimestral"]', 'Plantilla E2E Automatizada');

    // Guardar y abrir en editor
    await page.click('button:has-text("Guardar y Abrir en Editor")');

    // El modal debe cerrarse y el documento cargarse en Tiptap con el badge de Plantilla
    await expect(page.locator('text=Gestor de Plantillas e Importación DOCX')).not.toBeVisible();
    await expect(page.locator('header').locator('text=Plantilla')).toBeVisible();

    // El editor Tiptap debe contener los encabezados de las secciones de la plantilla
    const editor = page.locator('.ProseMirror');
    await expect(editor).toContainText('Introducción');
    await expect(editor).toContainText('Desarrollo / Contenido');
  });

  test('debe abrir panel de Asistente IA, generar propuesta y mostrar opciones de revisión', async ({ page }) => {
    await page.goto('/');

    // Abrir el asistente de IA desde la cabecera
    await page.click('button:has-text("Asistente IA")');

    // Verificar que el panel lateral abra
    await expect(page.locator('text=Asistente Documental')).toBeVisible();
    await expect(page.locator('text=Sección Objetivo')).toBeVisible();

    // Generar sección
    await page.click('button:has-text("Generar Sección")');

    // Debe mostrar la tarjeta de revisión con la propuesta y los botones Aceptar y Rechazar
    await expect(page.locator('text=Propuesta:')).toBeVisible();
    await expect(page.locator('button:has-text("Aceptar")')).toBeVisible();
    await expect(page.locator('button:has-text("Rechazar")')).toBeVisible();
  });

  test('debe mostrar botones de exportación DOCX y PDF en la cabecera', async ({ page }) => {
    await page.goto('/');

    // Verificar que los botones de exportación estén visibles y habilitados
    const btnDocx = page.locator('button[title*="Word (.docx)"]');
    const btnPdf = page.locator('button[title*="PDF"]');
    const btnPreview = page.locator('a[title*="Vista preliminar"]');

    await expect(btnDocx).toBeVisible();
    await expect(btnPdf).toBeVisible();
    await expect(btnPreview).toBeVisible();
  });
});
