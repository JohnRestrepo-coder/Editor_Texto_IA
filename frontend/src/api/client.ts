import type { Document, DocumentListItem, DocumentCreatePayload, DocumentUpdatePayload } from '../types/document';
import type {
  Template,
  TemplateListItem,
  TemplateCreatePayload,
  DocxInspectionResult,
} from '../types/template';

const API_BASE = '/api/v1';

export const api = {
  // Documentos
  async listDocuments(): Promise<DocumentListItem[]> {
    const res = await fetch(`${API_BASE}/documents`);
    if (!res.ok) throw new Error('Error al listar documentos');
    return res.json();
  },

  async getDocument(id: string): Promise<Document> {
    const res = await fetch(`${API_BASE}/documents/${id}`);
    if (!res.ok) throw new Error('Error al cargar documento');
    return res.json();
  },

  async createDocument(payload: DocumentCreatePayload): Promise<Document> {
    const res = await fetch(`${API_BASE}/documents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Error al crear documento');
    return res.json();
  },

  async updateDocument(id: string, payload: DocumentUpdatePayload): Promise<Document> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (res.status === 409) {
      const err = await res.json();
      throw new Error(err.detail?.message || 'Conflicto de versión al guardar el documento.');
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al guardar cambios');
    }

    return res.json();
  },

  async deleteDocument(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Error al eliminar documento');
  },

  // Plantillas
  async listTemplates(): Promise<TemplateListItem[]> {
    const res = await fetch(`${API_BASE}/templates`);
    if (!res.ok) throw new Error('Error al listar plantillas');
    return res.json();
  },

  async getTemplate(id: string): Promise<Template> {
    const res = await fetch(`${API_BASE}/templates/${id}`);
    if (!res.ok) throw new Error('Error al cargar plantilla');
    return res.json();
  },

  async createTemplate(payload: TemplateCreatePayload): Promise<Template> {
    const res = await fetch(`${API_BASE}/templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Error al crear plantilla');
    return res.json();
  },

  async updateTemplate(id: string, payload: Partial<TemplateCreatePayload>): Promise<Template> {
    const res = await fetch(`${API_BASE}/templates/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Error al actualizar plantilla');
    return res.json();
  },

  async deleteTemplate(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/templates/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Error al eliminar plantilla');
  },

  async importDocx(file: File): Promise<DocxInspectionResult> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/templates/import-docx`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al procesar el archivo Word (.docx)');
    }

    return res.json();
  },

  async createDocumentFromTemplate(templateId: string): Promise<Document> {
    const res = await fetch(`${API_BASE}/templates/${templateId}/create-document`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Error al instanciar documento desde plantilla');
    return res.json();
  },
};
