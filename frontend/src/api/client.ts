import type { Document, DocumentListItem, DocumentCreatePayload, DocumentUpdatePayload } from '../types/document';

const API_BASE = '/api/v1';

export const api = {
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
};
