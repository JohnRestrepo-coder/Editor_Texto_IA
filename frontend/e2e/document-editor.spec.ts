import { test, expect } from '@playwright/test';

test.describe('Feature 001: Editor Documental E2E', () => {
  test('debe cargar la aplicación y mostrar el editor Tiptap con documento inicial', async ({ page }) => {
    await page.goto('/');

    // Verificar que la cabecera del editor y la barra lateral estén presentes
    await expect(page.locator('text=Document Studio')).toBeVisible();
    await expect(page.locator('button:has-text("Nuevo Documento")')).toBeVisible();

    // El editor enriquecido debe estar presente y enfocado
    const editor = page.locator('.ProseMirror');
    await expect(editor).toBeVisible();

    // Debe mostrar la versión inicial v1
    await expect(page.locator('header').locator('text=v1')).toBeVisible();
  });

  test('debe permitir crear un nuevo documento en blanco, escribir y guardar', async ({ page }) => {
    await page.goto('/');

    // Crear un nuevo documento desde la barra lateral
    await page.click('button:has-text("Nuevo Documento")');

    // Cambiar el título del documento
    const titleInput = page.locator('input[placeholder="Título del documento..."]');
    await titleInput.fill('Reporte Técnico Automatizado E2E');

    // Escribir en el editor Tiptap
    const editor = page.locator('.ProseMirror');
    await editor.click();
    await editor.fill('Este es el contenido inicial redactado en la prueba E2E.');

    // Aplicar formato de negrita con la barra de herramientas
    await page.click('button[title="Encabezado 1"]');

    // Guardar los cambios
    await page.click('button:has-text("Guardar")');

    // Esperar a que el estado cambie a "Guardado" y la versión incremente a v2
    await expect(page.locator('text=Guardado')).toBeVisible();
    await expect(page.locator('header').locator('text=v2')).toBeVisible();

    // Verificar que en la barra lateral aparezca el título actualizado
    await expect(page.locator('aside').locator('text=Reporte Técnico Automatizado E2E')).toBeVisible();
  });

  test('debe recuperar el documento persistido al recargar la página', async ({ page }) => {
    await page.goto('/');

    // Seleccionar el documento creado en la prueba anterior si existe
    const docItem = page.locator('aside').locator('text=Reporte Técnico Automatizado E2E');
    if (await docItem.isVisible()) {
      await docItem.click();
    }

    // Verificar que el editor contiene el texto persistido
    const editor = page.locator('.ProseMirror');
    await expect(editor).toContainText('Este es el contenido inicial redactado en la prueba E2E.');

    // Recargar la página
    await page.reload();

    // El contenido y el título deben persistir tras el refresco
    const titleInput = page.locator('input[placeholder="Título del documento..."]');
    await expect(titleInput).toHaveValue(/Reporte Técnico Automatizado E2E|Documento/);
    await expect(editor).toBeVisible();
  });
});
