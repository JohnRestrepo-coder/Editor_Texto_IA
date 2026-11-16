import React, { useState, useEffect, useCallback } from 'react';
import { api } from './api/client';
import type { Document, DocumentListItem, DocumentContent } from './types/document';
import { Sidebar } from './components/Sidebar';
import { TiptapEditor } from './components/editor/TiptapEditor';
import { Save, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export const App: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [currentDoc, setCurrentDoc] = useState<Document | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState<DocumentContent | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saved' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [loading, setLoading] = useState(true);

  // Cargar lista de documentos
  const loadDocuments = useCallback(async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
      return docs;
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err.message || 'Error al conectar con el backend');
      return [];
    }
  }, []);

  // Crear nuevo documento libre
  const handleCreateNew = async () => {
    try {
      setIsSaving(true);
      const newDoc = await api.createDocument({
        title: 'Documento sin título',
      });
      await loadDocuments();
      setCurrentDoc(newDoc);
      setTitle(newDoc.title);
      setContent(newDoc.content);
      setSaveStatus('idle');
    } catch (err: any) {
      alert(err.message || 'Error al crear documento');
    } finally {
      setIsSaving(false);
    }
  };

  // Cargar un documento específico
  const handleSelectDoc = async (id: string) => {
    try {
      setLoading(true);
      const doc = await api.getDocument(id);
      setCurrentDoc(doc);
      setTitle(doc.title);
      setContent(doc.content);
      setSaveStatus('idle');
      setErrorMessage('');
    } catch (err: any) {
      alert(err.message || 'Error al cargar documento');
    } finally {
      setLoading(false);
    }
  };

  // Eliminar documento
  const handleDeleteDoc = async (id: string) => {
    try {
      await api.deleteDocument(id);
      const remaining = await loadDocuments();
      if (currentDoc?.id === id) {
        if (remaining.length > 0) {
          handleSelectDoc(remaining[0].id);
        } else {
          setCurrentDoc(null);
          setTitle('');
          setContent(null);
        }
      }
    } catch (err: any) {
      alert(err.message || 'Error al eliminar');
    }
  };

  // Guardar documento actual
  const handleSave = async () => {
    if (!currentDoc || !content) return;

    try {
      setIsSaving(true);
      setErrorMessage('');
      const updated = await api.updateDocument(currentDoc.id, {
        title: title.trim() || 'Documento sin título',
        content,
        expected_version: currentDoc.version,
      });

      setCurrentDoc(updated);
      setSaveStatus('saved');
      loadDocuments();

      setTimeout(() => {
        setSaveStatus('idle');
      }, 3000);
    } catch (err: any) {
      setSaveStatus('error');
      setErrorMessage(err.message || 'Error al guardar');
    } finally {
      setIsSaving(false);
    }
  };

  // Inicialización al montar
  useEffect(() => {
    (async () => {
      setLoading(true);
      const docs = await loadDocuments();
      if (docs.length > 0) {
        await handleSelectDoc(docs[0].id);
      } else {
        // Si no hay documentos, crear uno en blanco automáticamente para arranque directo
        const newDoc = await api.createDocument({
          title: 'Documento Libre Inicial',
        });
        await loadDocuments();
        setCurrentDoc(newDoc);
        setTitle(newDoc.title);
        setContent(newDoc.content);
      }
      setLoading(false);
    })();
  }, []);

  return (
    <div className="flex h-screen bg-slate-100 font-sans text-slate-800 antialiased overflow-hidden">
      {/* Panel Izquierdo: Documentos */}
      <Sidebar
        documents={documents}
        currentDocId={currentDoc?.id}
        onSelectDoc={handleSelectDoc}
        onCreateNew={handleCreateNew}
        onDeleteDoc={handleDeleteDoc}
      />

      {/* Área Central: Cabecera y Editor */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Cabecera Superior */}
        <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-4 flex-1 max-w-2xl">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Título del documento..."
              className="text-lg font-semibold text-slate-900 border-b border-transparent hover:border-slate-300 focus:border-blue-500 focus:outline-none px-1 py-0.5 w-full bg-transparent transition-colors"
            />
            {currentDoc && (
              <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200 whitespace-nowrap">
                v{currentDoc.version}
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            {saveStatus === 'saved' && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-medium">
                <CheckCircle2 size={16} /> Guardado
              </span>
            )}

            {saveStatus === 'error' && (
              <span className="flex items-center gap-1.5 text-xs text-red-600 font-medium" title={errorMessage}>
                <AlertCircle size={16} /> Conflicto / Error
              </span>
            )}

            <button
              onClick={handleSave}
              disabled={isSaving || !currentDoc}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-md shadow-sm transition-colors text-sm disabled:opacity-50"
            >
              {isSaving ? <Loader2 className="animate-spin" size={16} /> : <Save size={16} />}
              <span>{isSaving ? 'Guardando...' : 'Guardar'}</span>
            </button>
          </div>
        </header>

        {/* Mensaje de error / conflicto */}
        {errorMessage && (
          <div className="bg-red-50 border-b border-red-200 text-red-700 px-6 py-2 text-xs flex items-center justify-between">
            <span>{errorMessage}</span>
            <button onClick={() => setErrorMessage('')} className="underline text-red-800">Cerrar</button>
          </div>
        )}

        {/* Contenedor del Editor */}
        <section className="flex-1 p-6 overflow-hidden">
          {loading ? (
            <div className="h-full flex items-center justify-center text-slate-400">
              <Loader2 className="animate-spin mr-2" size={24} />
              <span>Cargando documento...</span>
            </div>
          ) : currentDoc && content ? (
            <TiptapEditor
              documentId={currentDoc.id}
              initialContent={content}
              onChange={(newContent) => setContent(newContent)}
            />
          ) : (
            <div className="h-full flex items-center justify-center text-slate-400">
              <span>Selecciona o crea un documento para comenzar</span>
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default App;
