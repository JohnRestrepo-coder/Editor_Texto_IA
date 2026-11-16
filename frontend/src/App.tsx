import React, { useState, useEffect, useCallback } from 'react';
import { api } from './api/client';
import type { Document, DocumentListItem, DocumentContent } from './types/document';
import { Sidebar } from './components/Sidebar';
import { TiptapEditor } from './components/editor/TiptapEditor';
import { TemplateModal } from './components/TemplateModal';
import { AIAssistantDrawer } from './components/AIAssistantDrawer';
import { AIGenerationPanel } from './components/AIGenerationPanel';
import { Save, CheckCircle2, AlertCircle, Loader2, Bookmark, Sparkles, Download, Eye, Layers } from 'lucide-react';

export const App: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [currentDoc, setCurrentDoc] = useState<Document | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState<DocumentContent | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saved' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const [isAIAssistantOpen, setIsAIAssistantOpen] = useState(false);
  const [activeAiBlock, setActiveAiBlock] = useState<{
    blockId: string;
    sectionTitle: string;
    instructions: string;
    mode: string;
  } | null>(null);
  const [isAIGenerationOpen, setIsAIGenerationOpen] = useState(false);
  const [isExporting, setIsExporting] = useState<'docx' | 'pdf' | null>(null);
  const [exportWarnings, setExportWarnings] = useState<string[]>([]);

  // Escuchar selección de bloque de IA para abrir panel de generación
  useEffect(() => {
    const handleBlockSelected = (e: Event) => {
      const customEvent = e as CustomEvent<{
        blockId: string;
        sectionTitle: string;
        instructions: string;
        mode: string;
      }>;
      setActiveAiBlock(customEvent.detail);
      setIsAIGenerationOpen(true);
      setIsAIAssistantOpen(false);
    };

    window.addEventListener('ai-block-selected', handleBlockSelected);
    return () => {
      window.removeEventListener('ai-block-selected', handleBlockSelected);
    };
  }, []);

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
        title: 'Documento Libre en Blanco',
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

  // Callback cuando se crea un documento desde plantilla
  const handleDocumentCreatedFromTemplate = async (doc: Document) => {
    await loadDocuments();
    setCurrentDoc(doc);
    setTitle(doc.title);
    setContent(doc.content);
    setSaveStatus('idle');
  };

  // Callback cuando la IA actualiza el documento tras aceptar una propuesta
  const handleDocumentUpdated = (doc: Document) => {
    setCurrentDoc(doc);
    setTitle(doc.title);
    setContent(doc.content);
    setSaveStatus('saved');
    loadDocuments();
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

  // Exportar a DOCX
  const handleExportDocx = async () => {
    if (!currentDoc) return;
    setIsExporting('docx');
    setExportWarnings([]);
    try {
      // Guardar cambios automáticamente si hay modificaciones
      if (content) {
        handleSave();
      }
      const { blob, filename, warnings } = await api.exportDocx(currentDoc.id, {
        title,
        content: content || undefined,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      if (warnings.length > 0) {
        setExportWarnings(warnings);
      }
    } catch (err: any) {
      alert(err.message || 'Error al exportar DOCX');
    } finally {
      setIsExporting(null);
    }
  };

  // Exportar a PDF
  const handleExportPdf = async () => {
    if (!currentDoc) return;
    setIsExporting('pdf');
    setExportWarnings([]);
    try {
      // Guardar cambios automáticamente si hay modificaciones
      if (content) {
        handleSave();
      }
      const { blob, filename, warnings } = await api.exportPdf(currentDoc.id, {
        title,
        content: content || undefined,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      if (warnings.length > 0) {
        setExportWarnings(warnings);
      }
    } catch (err: any) {
      alert(err.message || 'Error al exportar PDF');
    } finally {
      setIsExporting(null);
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
      {/* Panel Izquierdo: Documentos y Plantillas */}
      <Sidebar
        documents={documents}
        currentDocId={currentDoc?.id}
        onSelectDoc={handleSelectDoc}
        onCreateNew={handleCreateNew}
        onOpenTemplateModal={() => setIsTemplateModalOpen(true)}
        onDeleteDoc={handleDeleteDoc}
      />

      {/* Área Central: Cabecera y Editor */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Cabecera Superior */}
        <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-4 flex-1 max-w-2xl">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Título del documento..."
              className="text-lg font-semibold text-slate-900 border-b border-transparent hover:border-slate-300 focus:border-blue-500 focus:outline-none px-1 py-0.5 w-full bg-transparent transition-colors"
            />
            {currentDoc && (
              <div className="flex items-center gap-1.5">
                <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200 whitespace-nowrap">
                  v{currentDoc.version}
                </span>
                {currentDoc.template_id && (
                  <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded border border-blue-200 whitespace-nowrap flex items-center gap-1">
                    <Bookmark size={11} /> Plantilla
                  </span>
                )}
              </div>
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
              onClick={() => {
                setIsAIGenerationOpen((prev) => !prev);
                setIsAIAssistantOpen(false);
              }}
              disabled={!currentDoc}
              className={`flex items-center gap-1.5 font-medium px-3 py-2 rounded-md transition-colors text-sm cursor-pointer border ${
                isAIGenerationOpen
                  ? 'bg-indigo-600 text-white border-indigo-700 shadow-sm'
                  : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border-indigo-200'
              }`}
              title="Panel lateral de generación por bloques con IA"
            >
              <Sparkles size={16} />
              <span>Generar con IA</span>
            </button>

            <button
              onClick={() => {
                setIsAIAssistantOpen((prev) => !prev);
                setIsAIGenerationOpen(false);
              }}
              disabled={!currentDoc}
              className={`flex items-center gap-1.5 font-medium px-3 py-2 rounded-md transition-colors text-sm cursor-pointer border ${
                isAIAssistantOpen
                  ? 'bg-slate-700 text-white border-slate-800 shadow-sm'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-300'
              }`}
              title="Asistente general de documento"
            >
              <Layers size={15} />
              <span>Secciones</span>
            </button>

            <button
              onClick={handleSave}
              disabled={isSaving || !currentDoc}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-md shadow-xs transition-colors text-sm disabled:opacity-50 cursor-pointer"
            >
              {isSaving ? <Loader2 className="animate-spin" size={16} /> : <Save size={16} />}
              <span>{isSaving ? 'Guardando...' : 'Guardar'}</span>
            </button>

            {/* Acciones de Exportación (Feature 004) */}
            <div className="flex items-center gap-1.5 border-l border-slate-200 pl-3">
              <button
                onClick={handleExportDocx}
                disabled={!currentDoc || isExporting !== null}
                className="flex items-center gap-1 bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-2 rounded-md text-xs font-semibold border border-slate-300 transition cursor-pointer disabled:opacity-50"
                title="Descargar documento Word (.docx)"
              >
                {isExporting === 'docx' ? <Loader2 size={13} className="animate-spin" /> : <Download size={13} />}
                <span>DOCX</span>
              </button>
              <button
                onClick={handleExportPdf}
                disabled={!currentDoc || isExporting !== null}
                className="flex items-center gap-1 bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-2 rounded-md text-xs font-semibold border border-slate-300 transition cursor-pointer disabled:opacity-50"
                title="Descargar documento PDF"
              >
                {isExporting === 'pdf' ? <Loader2 size={13} className="animate-spin" /> : <Download size={13} />}
                <span>PDF</span>
              </button>
              <a
                href={currentDoc ? `/api/v1/exports/${currentDoc.id}/preview` : '#'}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 bg-slate-100 hover:bg-slate-200 text-slate-700 p-2 rounded-md text-xs border border-slate-300 transition"
                title="Vista preliminar de fidelidad de impresión"
              >
                <Eye size={14} />
              </a>
            </div>
          </div>
        </header>

        {/* Advertencias de elementos no soportados en exportación */}
        {exportWarnings.length > 0 && (
          <div className="bg-amber-50 border-b border-amber-200 text-amber-800 px-6 py-2 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span>⚠️ <strong>Aviso de Exportación:</strong> {exportWarnings.join(' · ')}</span>
            </div>
            <button onClick={() => setExportWarnings([])} className="underline text-amber-900 ml-4">Descartar</button>
          </div>
        )}

        {/* Mensaje de error / conflicto */}
        {errorMessage && (
          <div className="bg-red-50 border-b border-red-200 text-red-700 px-6 py-2 text-xs flex items-center justify-between">
            <span>{errorMessage}</span>
            <button onClick={() => setErrorMessage('')} className="underline text-red-800">Cerrar</button>
          </div>
        )}

        {/* Contenedor del Editor Tiptap */}
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

      {/* Modal de Plantillas e Importación DOCX */}
      <TemplateModal
        isOpen={isTemplateModalOpen}
        onClose={() => setIsTemplateModalOpen(false)}
        onDocumentCreated={handleDocumentCreatedFromTemplate}
      />

      {/* Panel Lateral de Asistente Clásico por Secciones */}
      <AIAssistantDrawer
        document={currentDoc}
        isOpen={isAIAssistantOpen}
        onClose={() => setIsAIAssistantOpen(false)}
        onDocumentUpdated={handleDocumentUpdated}
      />

      {/* Panel Lateral de Generación por Bloques con IA (Fase 2) */}
      <AIGenerationPanel
        document={currentDoc}
        isOpen={isAIGenerationOpen}
        onClose={() => setIsAIGenerationOpen(false)}
        activeBlock={activeAiBlock}
        onBlockInserted={() => {
          setTimeout(() => {
            handleSave();
          }, 300);
        }}
      />
    </div>
  );
};

export default App;
