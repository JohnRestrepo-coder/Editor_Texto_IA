import React, { useState, useRef } from 'react';
import {
  Sparkles,
  X,
  Upload,
  FileText,
  FileSpreadsheet,
  Trash2,
  Check,
  RotateCw,
  Edit3,
  AlertCircle,
  FileCode,
  File,
  Eye,
  EyeOff,
} from 'lucide-react';
import { api } from '../api/client';
import type { Document } from '../types/document';

interface AttachedSource {
  id: string;
  filename: string;
  file_type: string;
  char_count: number;
  extracted_text: string;
  success: boolean;
  error?: string | null;
}

interface AIGenerationPanelProps {
  document: Document | null;
  isOpen: boolean;
  onClose: () => void;
  activeBlock: {
    blockId: string;
    sectionTitle: string;
    instructions: string;
    mode: string;
  } | null;
  onBlockInserted?: () => void;
}

export const AIGenerationPanel: React.FC<AIGenerationPanelProps> = ({
  document: activeDoc,
  isOpen,
  onClose,
  activeBlock,
  onBlockInserted,
}) => {
  const [sources, setSources] = useState<AttachedSource[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const [instructions, setInstructions] = useState(activeBlock?.instructions || '');
  const [sectionTitle, setSectionTitle] = useState(activeBlock?.sectionTitle || 'Sección con IA');
  const [selectedMode, setSelectedMode] = useState<string>(activeBlock?.mode || 'draft');

  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [generatedResult, setGeneratedResult] = useState<{
    content: any;
    raw_text: string;
    provider: string;
    model: string;
  } | null>(null);

  const [isEditingResult, setIsEditingResult] = useState(false);
  const [editedText, setEditedText] = useState('');
  const [expandedSourceId, setExpandedSourceId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sincronizar datos si cambia el bloque activo
  React.useEffect(() => {
    if (activeBlock) {
      setSectionTitle(activeBlock.sectionTitle || 'Sección con IA');
      setInstructions(activeBlock.instructions || '');
      setSelectedMode(activeBlock.mode || 'draft');
    }
  }, [activeBlock]);

  if (!isOpen || !activeDoc) return null;

  // Cargar archivo y procesar extracción
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const res = await api.extractSource(file);

        const newSource: AttachedSource = {
          id: `source-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
          filename: res.filename,
          file_type: res.file_type,
          char_count: res.char_count,
          extracted_text: res.extracted_text,
          success: res.success,
          error: res.error,
        };

        setSources((prev) => [...prev, newSource]);
      }
    } catch (err: any) {
      setUploadError(err.message || 'Error al procesar el archivo seleccionado');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleRemoveSource = (id: string) => {
    setSources((prev) => prev.filter((s) => s.id !== id));
  };

  // Convertir contenido Tiptap en texto amigable para vista previa
  const extractReadableText = (content: any): string => {
    if (!content) return '';
    if (typeof content === 'string') return content;
    const lines: string[] = [];

    const recurse = (node: any) => {
      if (!node) return;
      if (node.type === 'text' && node.text) {
        lines.push(node.text);
      }
      if (node.content && Array.isArray(node.content)) {
        for (const child of node.content) {
          recurse(child);
        }
        if (node.type === 'paragraph' || node.type === 'heading' || node.type === 'listItem') {
          lines.push('\n');
        }
      }
    };

    recurse(content);
    return lines.join('').replace(/\n\s*\n/g, '\n\n').trim();
  };

  // Ejecutar generación con IA
  const handleGenerate = async () => {
    if (!activeBlock) {
      alert('Debes seleccionar o tener un bloque de IA activo en el documento.');
      return;
    }

    setIsGenerating(true);
    setGenerationError(null);
    setGeneratedResult(null);
    setIsEditingResult(false);

    try {
      // Concatenar texto de fuentes válidas
      const validSources = sources.filter((s) => s.success && s.extracted_text);
      const sourcesText = validSources
        .map((s) => `[ARCHIVO: ${s.filename}]\n${s.extracted_text}`)
        .join('\n\n');

      const res = await api.generateBlock({
        document_id: activeDoc.id,
        block_id: activeBlock.blockId,
        section_title: sectionTitle,
        user_instructions: instructions,
        mode: selectedMode,
        sources_text: sourcesText || undefined,
      });

      if (res.status === 'failed' || !res.content) {
        throw new Error(res.error_message || 'El servicio de IA no pudo generar la respuesta.');
      }

      setGeneratedResult({
        content: res.content,
        raw_text: res.raw_text,
        provider: res.provider,
        model: res.model,
      });

      setEditedText(extractReadableText(res.content));
    } catch (err: any) {
      setGenerationError(err.message || 'Error al conectar con el asistente de IA');
    } finally {
      setIsGenerating(false);
    }
  };

  // Insertar resultado en el documento reemplazando exactamente el bloque
  const handleInsertText = () => {
    if (!activeBlock || !generatedResult) return;

    let contentToInsert = generatedResult.content;

    // Si el usuario editó manualmente el texto, generar párrafos a partir de las líneas editadas
    if (isEditingResult && editedText.trim()) {
      const paragraphs = editedText
        .split('\n\n')
        .map((p) => p.trim())
        .filter(Boolean)
        .map((p) => ({
          type: 'paragraph',
          content: [{ type: 'text', text: p }],
        }));

      contentToInsert = {
        type: 'doc',
        content: paragraphs,
      };
    }

    // Disparar evento para que Tiptap reemplace el bloque
    window.dispatchEvent(
      new CustomEvent('replace-ai-block', {
        detail: {
          blockId: activeBlock.blockId,
          content: contentToInsert,
        },
      })
    );

    if (onBlockInserted) {
      onBlockInserted();
    }

    // Limpiar resultado y cerrar panel
    setGeneratedResult(null);
    onClose();
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return <FileText className="text-red-500" size={16} />;
      case 'docx':
        return <FileText className="text-blue-500" size={16} />;
      case 'excel':
      case 'xlsx':
      case 'xls':
        return <FileSpreadsheet className="text-emerald-600" size={16} />;
      case 'csv':
        return <FileCode className="text-teal-600" size={16} />;
      default:
        return <File className="text-slate-500" size={16} />;
    }
  };

  return (
    <aside className="w-[500px] bg-white border-l border-slate-200 shadow-xl flex flex-col h-screen z-30 transition-all duration-300">
      {/* Cabecera del Panel */}
      <div className="p-4 border-b border-slate-200 bg-gradient-to-r from-indigo-50/70 to-purple-50/70 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-xs">
            <Sparkles size={16} />
          </div>
          <div>
            <h2 className="font-bold text-slate-800 text-sm">Generación con IA por Bloque</h2>
            <p className="text-xs text-indigo-700 font-medium">
              {activeBlock ? `Bloque: "${sectionTitle}"` : 'Sin bloque seleccionado'}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-700 p-1 rounded-md hover:bg-slate-200/50 transition-colors"
        >
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {/* ÁREA A: Fuentes de Información */}
        <section className="bg-slate-50 border border-slate-200 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
              <span>A. Fuentes de Información</span>
              <span className="text-[10px] bg-indigo-100 text-indigo-800 px-1.5 py-0.2 rounded font-normal">
                {sources.length}
              </span>
            </h3>
            <span className="text-[11px] text-slate-500">PDF, DOCX, XLSX, XLS, CSV, TXT</span>
          </div>

          <p className="text-xs text-slate-600 mb-3 leading-relaxed">
            Sube documentos para que la IA extraiga su contenido y los utilice como base real de redacción.
          </p>

          {/* Botón de carga */}
          <div className="flex items-center gap-2 mb-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              multiple
              accept=".pdf,.docx,.xlsx,.xls,.csv,.txt,.md"
              className="hidden"
              id="source-file-upload"
            />
            <label
              htmlFor="source-file-upload"
              className={`flex-1 flex items-center justify-center gap-2 border-2 border-dashed border-slate-300 hover:border-indigo-400 bg-white hover:bg-indigo-50/30 text-slate-700 text-xs font-semibold py-2.5 px-3 rounded-lg cursor-pointer transition-colors ${
                isUploading ? 'opacity-50 pointer-events-none' : ''
              }`}
            >
              <Upload size={14} className="text-indigo-600" />
              <span>{isUploading ? 'Extrayendo contenido...' : 'Cargar archivos desde el computador'}</span>
            </label>
          </div>

          {uploadError && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-xs p-2.5 rounded-lg mb-3 flex items-start gap-2">
              <AlertCircle size={14} className="shrink-0 mt-0.5" />
              <span>{uploadError}</span>
            </div>
          )}

          {/* Lista de fuentes cargadas */}
          {sources.length > 0 && (
            <div className="space-y-2 mt-2">
              {sources.map((source) => (
                <div
                  key={source.id}
                  className={`border rounded-lg p-2.5 text-xs transition-colors ${
                    source.success ? 'bg-white border-slate-200' : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0">
                      {getFileIcon(source.file_type)}
                      <span className="font-medium text-slate-800 truncate" title={source.filename}>
                        {source.filename}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      {source.success ? (
                        <>
                          <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                            {source.char_count.toLocaleString()} caracteres
                          </span>
                          <button
                            type="button"
                            onClick={() =>
                              setExpandedSourceId(expandedSourceId === source.id ? null : source.id)
                            }
                            title="Ver contenido extraído"
                            className="text-slate-400 hover:text-indigo-600 p-1 rounded"
                          >
                            {expandedSourceId === source.id ? <EyeOff size={13} /> : <Eye size={13} />}
                          </button>
                        </>
                      ) : (
                        <span className="text-[10px] text-red-600 font-semibold">Error de lectura</span>
                      )}
                      <button
                        type="button"
                        onClick={() => handleRemoveSource(source.id)}
                        className="text-slate-400 hover:text-red-500 p-1 rounded transition-colors"
                        title="Eliminar fuente"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </div>

                  {/* Vista preliminar del texto extraído */}
                  {expandedSourceId === source.id && source.success && (
                    <div className="mt-2 pt-2 border-t border-slate-100">
                      <p className="text-[11px] font-semibold text-slate-500 mb-1">Contenido extraído para la IA:</p>
                      <div className="bg-slate-50 border border-slate-200 rounded p-2 text-[11px] text-slate-700 max-h-36 overflow-y-auto whitespace-pre-wrap font-mono">
                        {source.extracted_text}
                      </div>
                    </div>
                  )}

                  {!source.success && source.error && (
                    <p className="text-[11px] text-red-600 mt-1">{source.error}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ÁREA B: Instrucciones o Prompt */}
        <section className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
            B. Instrucciones y Propósito
          </h3>

          {/* Selección de modo */}
          <div className="flex flex-wrap gap-1.5 mb-3">
            {[
              { id: 'draft', label: 'Redacción', icon: '📝' },
              { id: 'review', label: 'Corrección', icon: '🔍' },
              { id: 'summary', label: 'Resumen', icon: '📊' },
              { id: 'expand', label: 'Ampliación', icon: '📈' },
              { id: 'analyze', label: 'Análisis', icon: '🧠' },
            ].map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => setSelectedMode(m.id)}
                className={`text-xs px-2.5 py-1 rounded-md font-medium transition-colors flex items-center gap-1 ${
                  selectedMode === m.id
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                }`}
              >
                <span>{m.icon}</span>
                <span>{m.label}</span>
              </button>
            ))}
          </div>

          {/* Área de texto de instrucciones */}
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Instrucciones libres para la IA:
          </label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            rows={4}
            placeholder="Ejemplo: Redacta el análisis del mercado del emprendimiento utilizando la información de los archivos adjuntos. Organiza el contenido en párrafos formales, utiliza un tono académico y no inventes cifras. Si falta información, señala los datos pendientes."
            className="w-full text-xs text-slate-800 border border-slate-300 hover:border-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none rounded-lg p-3 leading-relaxed transition-colors"
          />
        </section>

        {/* ÁREA C: Botón Principal de Generación */}
        <section>
          <button
            type="button"
            onClick={handleGenerate}
            disabled={isGenerating || !activeBlock}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 px-4 rounded-xl shadow-md transition-all cursor-pointer disabled:opacity-50 text-sm"
          >
            {isGenerating ? (
              <>
                <RotateCw className="animate-spin" size={16} />
                <span>Generando con IA... Analizando fuentes</span>
              </>
            ) : (
              <>
                <Sparkles size={16} className="text-yellow-300" />
                <span>Generar contenido con IA</span>
              </>
            )}
          </button>

          {generationError && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-xs p-3 rounded-lg mt-3 flex items-start gap-2">
              <AlertCircle size={15} className="shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold">Fallo en la generación:</p>
                <p>{generationError}</p>
                <button
                  onClick={handleGenerate}
                  className="mt-1 text-xs text-red-800 underline font-semibold"
                >
                  Volver a intentar
                </button>
              </div>
            </div>
          )}
        </section>

        {/* ÁREA D: Visualización del Resultado (Fase 2.3) */}
        {generatedResult && (
          <section className="bg-indigo-50/50 border border-indigo-200 rounded-xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                <h3 className="text-xs font-bold text-indigo-950 uppercase tracking-wider">
                  Resultado Generado (Vista Previa)
                </h3>
              </div>
              <span className="text-[10px] bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded font-mono">
                {generatedResult.model}
              </span>
            </div>

            {/* Vista previa editable o formateada */}
            {isEditingResult ? (
              <textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                rows={8}
                className="w-full text-xs text-slate-800 bg-white border border-indigo-300 rounded-lg p-3 font-sans leading-relaxed focus:outline-indigo-500"
              />
            ) : (
              <div className="bg-white border border-indigo-100 rounded-lg p-3 max-h-72 overflow-y-auto text-xs text-slate-800 leading-relaxed whitespace-pre-wrap">
                {editedText || extractReadableText(generatedResult.content)}
              </div>
            )}

            {/* 4 Acciones Requeridas: Insertar texto, Regenerar, Editar resultado, Descartar */}
            <div className="grid grid-cols-2 gap-2 pt-1">
              <button
                type="button"
                onClick={handleInsertText}
                className="col-span-2 flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-2.5 px-3 rounded-lg shadow-xs transition-colors cursor-pointer"
              >
                <Check size={14} />
                <span>Insertar texto en el documento</span>
              </button>

              <button
                type="button"
                onClick={handleGenerate}
                disabled={isGenerating}
                className="flex items-center justify-center gap-1.5 bg-white hover:bg-slate-50 text-indigo-700 border border-indigo-200 text-xs font-semibold py-2 px-3 rounded-lg transition-colors cursor-pointer"
              >
                <RotateCw size={13} />
                <span>Regenerar</span>
              </button>

              <button
                type="button"
                onClick={() => setIsEditingResult((prev) => !prev)}
                className="flex items-center justify-center gap-1.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 text-xs font-semibold py-2 px-3 rounded-lg transition-colors cursor-pointer"
              >
                <Edit3 size={13} />
                <span>{isEditingResult ? 'Ver formato' : 'Editar resultado'}</span>
              </button>

              <button
                type="button"
                onClick={() => setGeneratedResult(null)}
                className="col-span-2 flex items-center justify-center gap-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-medium py-1.5 px-3 rounded-lg transition-colors cursor-pointer"
              >
                <Trash2 size={13} />
                <span>Descartar propuesta</span>
              </button>
            </div>
          </section>
        )}
      </div>
    </aside>
  );
};
