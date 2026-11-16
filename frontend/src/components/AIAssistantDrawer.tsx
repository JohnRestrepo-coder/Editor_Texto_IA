import React, { useState, useEffect, useCallback } from 'react';
import type { Document, DocumentContent } from '../types/document';
import type { GenerationResponse } from '../types/generation';
import { api } from '../api/client';

interface AIAssistantDrawerProps {
  document: Document | null;
  isOpen: boolean;
  onClose: () => void;
  onDocumentUpdated: (doc: Document) => void;
}

export const AIAssistantDrawer: React.FC<AIAssistantDrawerProps> = ({
  document,
  isOpen,
  onClose,
  onDocumentUpdated,
}) => {
  const [availableSections, setAvailableSections] = useState<string[]>([]);
  const [selectedSection, setSelectedSection] = useState<string>('');
  const [userInstructions, setUserInstructions] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGeneratingAll, setIsGeneratingAll] = useState(false);
  const [currentProposal, setCurrentProposal] = useState<GenerationResponse | null>(null);
  const [recentGenerations, setRecentGenerations] = useState<GenerationResponse[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Extraer encabezados H2 del documento actual como secciones disponibles
  useEffect(() => {
    if (!document || !document.content || !document.content.content) {
      setAvailableSections(['Introducción', 'Desarrollo', 'Conclusiones']);
      setSelectedSection('Introducción');
      return;
    }

    const headings: string[] = [];
    for (const node of document.content.content) {
      if (node.type === 'heading' && node.content) {
        const text = node.content.map((c) => c.text || '').join('').trim();
        if (text) headings.push(text);
      }
    }

    if (headings.length > 0) {
      setAvailableSections(headings);
      setSelectedSection((prev) => (headings.includes(prev) ? prev : headings[0]));
    } else {
      setAvailableSections(['Sección Principal']);
      setSelectedSection('Sección Principal');
    }
  }, [document]);

  // Cargar historial de propuestas para el documento
  const loadHistory = useCallback(async () => {
    if (!document) return;
    try {
      const history = await api.listDocumentGenerations(document.id);
      setRecentGenerations(history);
      if (history.length > 0 && !currentProposal) {
        // Mostrar la última propuesta completada o pendiente de revisión
        const pending = history.find((h) => h.status === 'completed');
        if (pending) setCurrentProposal(pending);
      }
    } catch (err) {
      console.error('Error al cargar historial de generaciones:', err);
    }
  }, [document, currentProposal]);

  useEffect(() => {
    if (isOpen && document) {
      loadHistory();
    }
  }, [isOpen, document, loadHistory]);

  if (!isOpen || !document) return null;

  // Generar propuesta para una sección
  const handleGenerateSection = async () => {
    if (!selectedSection) return;
    setIsGenerating(true);
    setErrorMsg(null);
    try {
      const res = await api.generateSection({
        document_id: document.id,
        section_id: selectedSection,
        section_title: selectedSection,
        user_instructions: userInstructions,
        expected_document_version: document.version,
      });
      setCurrentProposal(res);
      await loadHistory();
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Error al generar sección');
    } finally {
      setIsGenerating(false);
    }
  };

  // Orquestar generación completa de todas las secciones
  const handleGenerateAll = async () => {
    setIsGeneratingAll(true);
    setErrorMsg(null);
    try {
      const res = await api.generateAllSections(document.id, {
        instructions: userInstructions || 'Generar contenido coherente para todo el documento',
        expected_document_version: document.version,
      });
      if (res.generations.length > 0) {
        setCurrentProposal(res.generations[res.generations.length - 1]);
      }
      await loadHistory();
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Error en la generación completa');
    } finally {
      setIsGeneratingAll(false);
    }
  };

  // Aceptar propuesta y aplicarla al documento
  const handleAcceptProposal = async () => {
    if (!currentProposal) return;
    setErrorMsg(null);
    try {
      const updatedDoc = await api.acceptGeneration(
        currentProposal.generation_id,
        document.version
      );
      onDocumentUpdated(updatedDoc);
      setCurrentProposal((prev) => (prev ? { ...prev, status: 'accepted' } : null));
      await loadHistory();
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Error al aceptar propuesta');
    }
  };

  // Rechazar propuesta sin tocar el documento
  const handleRejectProposal = async () => {
    if (!currentProposal) return;
    setErrorMsg(null);
    try {
      const rejected = await api.rejectGeneration(currentProposal.generation_id);
      setCurrentProposal(rejected);
      await loadHistory();
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Error al rechazar propuesta');
    }
  };

  // Extraer texto plano de la propuesta para preview amigable
  const extractPreviewText = (content: DocumentContent | null | Record<string, unknown>): string => {
    if (!content || !Array.isArray(content.content)) return 'Sin contenido generado.';
    const paragraphs: string[] = [];
    for (const node of content.content) {
      if (typeof node === 'object' && node !== null) {
        const n = node as { type?: string; content?: Array<{ text?: string }> };
        if (n.content && Array.isArray(n.content)) {
          const t = n.content.map((c) => c.text || '').join('');
          if (t) paragraphs.push(t);
        }
      }
    }
    return paragraphs.join('\n\n') || 'Estructura de bloques generada.';
  };

  return (
    <div
      role="dialog"
      aria-label="Panel Asistente IA"
      className="fixed inset-y-0 right-0 w-96 max-w-full bg-white shadow-2xl border-l border-slate-200 z-50 flex flex-col transition-all"
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
        <div className="flex items-center gap-2">
          <span className="p-1.5 bg-indigo-100 text-indigo-700 rounded-md font-bold text-sm">
            ✨ IA
          </span>
          <div>
            <h2 className="font-semibold text-slate-800 text-sm">Asistente Documental</h2>
            <p className="text-xs text-slate-500">Generación selectiva por sección</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-200 transition"
          aria-label="Cerrar panel IA"
        >
          ✕
        </button>
      </div>

      {/* Contenido scrollable */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {errorMsg && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-md">
            ⚠️ {errorMsg}
          </div>
        )}

        {/* Selector de sección */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
            Sección Objetivo
          </label>
          <select
            value={selectedSection}
            onChange={(e) => setSelectedSection(e.target.value)}
            disabled={isGenerating || isGeneratingAll}
            className="w-full text-sm border border-slate-300 rounded-md p-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {availableSections.map((sec, idx) => (
              <option key={idx} value={sec}>
                📌 {sec}
              </option>
            ))}
          </select>
        </div>

        {/* Instrucciones del usuario */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
            Instrucciones para la IA
          </label>
          <textarea
            rows={3}
            placeholder="Ej: Enfatizar antecedentes, usar tono corporativo, resumir en 3 puntos clave..."
            value={userInstructions}
            onChange={(e) => setUserInstructions(e.target.value)}
            disabled={isGenerating || isGeneratingAll}
            className="w-full text-sm border border-slate-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder-slate-400"
          />
        </div>

        {/* Botones de acción */}
        <div className="flex gap-2">
          <button
            onClick={handleGenerateSection}
            disabled={isGenerating || isGeneratingAll || !selectedSection}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-medium py-2 px-3 rounded-md text-xs shadow-sm flex items-center justify-center gap-1.5 transition"
          >
            {isGenerating ? (
              <>
                <span className="animate-spin text-sm">⏳</span> Generando...
              </>
            ) : (
              <>⚡ Generar Sección</>
            )}
          </button>
          <button
            onClick={handleGenerateAll}
            disabled={isGenerating || isGeneratingAll}
            title="Genera todas las secciones del documento respetando dependencias"
            className="bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 font-medium py-2 px-3 rounded-md text-xs transition"
          >
            {isGeneratingAll ? '⏳...' : '🌐 Generar Todo'}
          </button>
        </div>

        {/* Tarjeta de Revisión de Propuesta */}
        {currentProposal && (
          <div className="border border-indigo-200 bg-indigo-50/40 rounded-lg p-3.5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-indigo-900">
                Propuesta: {currentProposal.section_title}
              </span>
              <span
                className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase ${
                  currentProposal.status === 'accepted'
                    ? 'bg-emerald-100 text-emerald-800'
                    : currentProposal.status === 'rejected'
                    ? 'bg-rose-100 text-rose-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {currentProposal.status === 'completed'
                  ? 'Pendiente de Revisión'
                  : currentProposal.status === 'accepted'
                  ? 'Aceptada'
                  : 'Rechazada'}
              </span>
            </div>

            {/* Vista previa del contenido */}
            <div className="bg-white border border-slate-200 rounded p-2.5 max-h-48 overflow-y-auto text-xs text-slate-700 whitespace-pre-line leading-relaxed shadow-inner">
              {extractPreviewText(currentProposal.content)}
            </div>

            {/* Metadatos de auditoría */}
            <div className="flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-slate-500 border-t border-indigo-100 pt-2">
              <span>Modelo: <strong>{currentProposal.metadata_info.model}</strong></span>
              <span>Latencia: <strong>{currentProposal.metadata_info.latency_ms} ms</strong></span>
              <span>Prompt: <strong>{currentProposal.metadata_info.prompt_version}</strong></span>
            </div>

            {/* Acciones de revisión: Aceptar / Rechazar / Regenerar aisladamente */}
            {currentProposal.status === 'completed' ? (
              <div className="flex items-center gap-2 pt-1">
                <button
                  onClick={handleAcceptProposal}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-1.5 px-2 rounded text-xs transition flex items-center justify-center gap-1"
                >
                  ✓ Aceptar
                </button>
                <button
                  onClick={handleRejectProposal}
                  className="bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium py-1.5 px-2 rounded text-xs transition"
                >
                  ✕ Rechazar
                </button>
                <button
                  onClick={handleGenerateSection}
                  disabled={isGenerating}
                  className="border border-indigo-300 hover:bg-indigo-100 text-indigo-700 font-medium py-1.5 px-2 rounded text-xs transition"
                  title="Regenerar esta sección aisladamente"
                >
                  🔄
                </button>
              </div>
            ) : (
              <div className="pt-1">
                <button
                  onClick={handleGenerateSection}
                  disabled={isGenerating}
                  className="w-full border border-indigo-300 hover:bg-indigo-50 text-indigo-700 font-medium py-1.5 rounded text-xs transition flex items-center justify-center gap-1"
                >
                  🔄 Regenerar propuesta
                </button>
              </div>
            )}
          </div>
        )}

        {/* Historial de Propuestas Recientes */}
        {recentGenerations.length > 0 && (
          <div className="space-y-2 pt-2 border-t border-slate-200">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Historial de Auditoría
            </h3>
            <div className="space-y-1.5 max-h-40 overflow-y-auto">
              {recentGenerations.map((gen) => (
                <div
                  key={gen.generation_id}
                  onClick={() => setCurrentProposal(gen)}
                  className={`p-2 rounded text-xs border cursor-pointer transition flex items-center justify-between ${
                    currentProposal?.generation_id === gen.generation_id
                      ? 'border-indigo-500 bg-indigo-50/50'
                      : 'border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <div>
                    <span className="font-medium text-slate-800">{gen.section_title}</span>
                    <span className="text-[10px] text-slate-400 block">
                      {new Date(gen.created_at).toLocaleTimeString()} · {gen.metadata_info.provider}
                    </span>
                  </div>
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded uppercase font-semibold ${
                      gen.status === 'accepted'
                        ? 'bg-emerald-100 text-emerald-700'
                        : gen.status === 'rejected'
                        ? 'bg-rose-100 text-rose-700'
                        : 'bg-amber-100 text-amber-700'
                    }`}
                  >
                    {gen.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
