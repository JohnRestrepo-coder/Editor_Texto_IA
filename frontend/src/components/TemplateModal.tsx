import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { TemplateListItem, Section, DocxInspectionResult } from '../types/template';
import type { Document } from '../types/document';
import {
  FileText,
  Upload,
  Plus,
  Trash2,
  X,
  FileCheck,
  AlertTriangle,
  Layers,
  ArrowRight,
  Loader2,
  Check
} from 'lucide-react';

interface TemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDocumentCreated: (doc: Document) => void;
}

export const TemplateModal: React.FC<TemplateModalProps> = ({
  isOpen,
  onClose,
  onDocumentCreated,
}) => {
  const [activeTab, setActiveTab] = useState<'browse' | 'import' | 'create'>('browse');
  const [templates, setTemplates] = useState<TemplateListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Estados para creación / edición de plantilla
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [sections, setSections] = useState<Section[]>([
    {
      id: 'sec_1',
      title: 'Introducción',
      position: 0,
      required: true,
      instructions: 'Contexto general y propósito del documento',
      generation_enabled: true,
      depends_on: [],
    },
    {
      id: 'sec_2',
      title: 'Desarrollo / Contenido',
      position: 1,
      required: true,
      instructions: 'Cuerpo principal y análisis',
      generation_enabled: true,
      depends_on: ['sec_1'],
    },
    {
      id: 'sec_3',
      title: 'Conclusiones y Próximos Pasos',
      position: 2,
      required: true,
      instructions: 'Resumen de conclusiones y recomendaciones',
      generation_enabled: true,
      depends_on: ['sec_2'],
    },
  ]);

  // Estados para importación DOCX
  const [inspectionResult, setInspectionResult] = useState<DocxInspectionResult | null>(null);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const list = await api.listTemplates();
      setTemplates(list);
    } catch (err: any) {
      setErrorMessage(err.message || 'Error al cargar plantillas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadTemplates();
      setErrorMessage('');
      setInspectionResult(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  // Manejar importación de archivo DOCX
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.docx')) {
      setErrorMessage('Por favor selecciona un archivo con extensión .docx');
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage('');
      const result = await api.importDocx(file);
      setInspectionResult(result);
      await loadTemplates();
    } catch (err: any) {
      setErrorMessage(err.message || 'Error al importar archivo DOCX');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Crear documento desde plantilla seleccionada
  const handleUseTemplate = async (templateId: string) => {
    try {
      setIsSubmitting(true);
      const newDoc = await api.createDocumentFromTemplate(templateId);
      onDocumentCreated(newDoc);
      onClose();
    } catch (err: any) {
      setErrorMessage(err.message || 'Error al crear documento desde plantilla');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Guardar plantilla nativa
  const handleSaveNativeTemplate = async () => {
    if (!name.trim()) {
      setErrorMessage('El nombre de la plantilla es obligatorio');
      return;
    }

    try {
      setIsSubmitting(true);
      const created = await api.createTemplate({
        name: name.trim(),
        description: description.trim(),
        source_type: 'native',
        sections,
      });

      // Crear documento inmediatamente
      const doc = await api.createDocumentFromTemplate(created.id);
      onDocumentCreated(doc);
      onClose();
    } catch (err: any) {
      setErrorMessage(err.message || 'Error al guardar plantilla');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Manejo de secciones
  const addSection = () => {
    const newId = `sec_${Date.now()}`;
    setSections([
      ...sections,
      {
        id: newId,
        title: `Nueva Sección ${sections.length + 1}`,
        position: sections.length,
        required: true,
        instructions: '',
        generation_enabled: true,
        depends_on: [],
      },
    ]);
  };

  const removeSection = (index: number) => {
    const updated = sections.filter((_, i) => i !== index);
    setSections(updated.map((s, idx) => ({ ...s, position: idx })));
  };

  const updateSectionField = (index: number, field: keyof Section, val: any) => {
    const updated = [...sections];
    updated[index] = { ...updated[index], [field]: val };
    setSections(updated);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Cabecera del Modal */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2 text-slate-800 font-bold text-lg">
            <Layers className="text-blue-600" size={22} />
            <span>Gestor de Plantillas e Importación DOCX</span>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-md"
          >
            <X size={20} />
          </button>
        </div>

        {/* Pestañas de Navegación */}
        <div className="flex border-b border-slate-200 bg-white px-6">
          <button
            onClick={() => setActiveTab('browse')}
            className={`py-3 px-4 font-medium text-sm border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'browse'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileText size={16} />
            <span>Plantillas Disponibles ({templates.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('import')}
            className={`py-3 px-4 font-medium text-sm border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'import'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Upload size={16} />
            <span>Importar Word (.docx)</span>
          </button>

          <button
            onClick={() => setActiveTab('create')}
            className={`py-3 px-4 font-medium text-sm border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'create'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Plus size={16} />
            <span>Diseñar Plantilla Nativa</span>
          </button>
        </div>

        {/* Mensajes de Error */}
        {errorMessage && (
          <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-md flex items-center gap-2">
            <AlertTriangle size={16} />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Contenido según Pestaña */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Pestaña 1: Explorar Plantillas */}
          {activeTab === 'browse' && (
            <div>
              {loading ? (
                <div className="py-12 flex flex-col items-center justify-center text-slate-400">
                  <Loader2 className="animate-spin mb-2" size={24} />
                  <span>Cargando plantillas...</span>
                </div>
              ) : templates.length === 0 ? (
                <div className="py-12 text-center text-slate-500 space-y-3">
                  <p>Aún no hay plantillas registradas.</p>
                  <div className="flex justify-center gap-3">
                    <button
                      onClick={() => setActiveTab('create')}
                      className="bg-blue-600 text-white text-xs px-3 py-2 rounded-md hover:bg-blue-500 font-medium"
                    >
                      Crear Plantilla Nativa
                    </button>
                    <button
                      onClick={() => setActiveTab('import')}
                      className="bg-slate-200 text-slate-700 text-xs px-3 py-2 rounded-md hover:bg-slate-300 font-medium"
                    >
                      Importar archivo DOCX
                    </button>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {templates.map((tpl) => (
                    <div
                      key={tpl.id}
                      className="border border-slate-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between bg-white"
                    >
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span
                            className={`text-xs px-2 py-0.5 rounded font-semibold uppercase tracking-wider ${
                              tpl.source_type === 'docx'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}
                          >
                            {tpl.source_type === 'docx' ? 'Word DOCX' : 'Nativa'}
                          </span>
                          <span className="text-xs text-slate-400">
                            {tpl.sections_count} secciones
                          </span>
                        </div>
                        <h4 className="font-bold text-slate-800 text-base mb-1">{tpl.name}</h4>
                        <p className="text-xs text-slate-500 line-clamp-2">
                          {tpl.description || 'Sin descripción'}
                        </p>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-end">
                        <button
                          onClick={() => handleUseTemplate(tpl.id)}
                          disabled={isSubmitting}
                          className="flex items-center gap-1.5 text-xs bg-blue-600 hover:bg-blue-500 text-white font-medium py-1.5 px-3 rounded shadow-xs transition-colors"
                        >
                          {isSubmitting ? (
                            <Loader2 className="animate-spin" size={14} />
                          ) : (
                            <ArrowRight size={14} />
                          )}
                          <span>Usar en Editor</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Pestaña 2: Importar DOCX y Mapeo */}
          {activeTab === 'import' && (
            <div className="space-y-6">
              {!inspectionResult ? (
                <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors bg-slate-50">
                  <Upload className="mx-auto text-slate-400 mb-3" size={36} />
                  <h4 className="font-bold text-slate-700 text-base mb-1">
                    Cargar archivo de plantilla Word (.docx)
                  </h4>
                  <p className="text-xs text-slate-500 mb-4 max-w-md mx-auto">
                    El documento original se conservará intacto. El sistema analizará títulos,
                    secciones y tablas para configurar la estructura editable.
                  </p>
                  <label className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-md shadow-xs cursor-pointer text-sm">
                    {isSubmitting ? <Loader2 className="animate-spin" size={16} /> : <Upload size={16} />}
                    <span>{isSubmitting ? 'Analizando DOCX...' : 'Seleccionar archivo .docx'}</span>
                    <input
                      type="file"
                      accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                      onChange={handleFileUpload}
                      disabled={isSubmitting}
                      className="hidden"
                    />
                  </label>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg flex items-start gap-3">
                    <FileCheck className="text-emerald-600 mt-0.5" size={20} />
                    <div className="flex-1">
                      <h4 className="font-bold text-emerald-900 text-sm">
                        ¡Archivo inspeccionado con éxito!
                      </h4>
                      <p className="text-xs text-emerald-700 mt-0.5">
                        Documento: <strong>{inspectionResult.filename}</strong> · Secciones detectadas: <strong>{inspectionResult.detected_sections.length}</strong> · Tablas: <strong>{inspectionResult.tables_count}</strong>
                      </p>
                    </div>
                  </div>

                  {inspectionResult.unsupported_elements.length > 0 && (
                    <div className="p-3 bg-amber-50 border border-amber-200 text-amber-800 text-xs rounded-md">
                      {inspectionResult.unsupported_elements.map((warn, i) => (
                        <p key={i}>⚠️ {warn}</p>
                      ))}
                    </div>
                  )}

                  <div>
                    <h5 className="font-semibold text-slate-800 text-sm mb-2">
                      Secciones identificadas para el editor:
                    </h5>
                    <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                      {inspectionResult.detected_sections.map((sec, idx) => (
                        <div
                          key={sec.id}
                          className="p-2.5 bg-slate-50 border border-slate-200 rounded flex items-center justify-between text-xs"
                        >
                          <div>
                            <span className="font-semibold text-slate-800">
                              {idx + 1}. {sec.title}
                            </span>
                            <p className="text-slate-500 text-[11px] mt-0.5">
                              {sec.instructions}
                            </p>
                          </div>
                          <span className="bg-slate-200 text-slate-600 px-2 py-0.5 rounded text-[10px]">
                            {sec.required ? 'Obligatoria' : 'Opcional'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex justify-end gap-3 pt-3 border-t border-slate-200">
                    <button
                      onClick={() => setInspectionResult(null)}
                      className="px-4 py-2 border border-slate-300 text-slate-700 rounded-md text-xs hover:bg-slate-50"
                    >
                      Cargar otro archivo
                    </button>
                    <button
                      onClick={() => handleUseTemplate(inspectionResult.template_id)}
                      disabled={isSubmitting}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md text-xs font-semibold flex items-center gap-1.5"
                    >
                      {isSubmitting ? <Loader2 className="animate-spin" size={14} /> : <Check size={14} />}
                      <span>Abrir Documento en Editor</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Pestaña 3: Diseñar Plantilla Nativa */}
          {activeTab === 'create' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Nombre de la Plantilla *
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Ej. Plan de Trabajo Trimestral"
                    className="w-full text-xs p-2 border border-slate-300 rounded focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Descripción
                  </label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Objetivo o alcance de esta plantilla"
                    className="w-full text-xs p-2 border border-slate-300 rounded focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-700">
                    Estructura de Secciones ({sections.length})
                  </span>
                  <button
                    onClick={addSection}
                    type="button"
                    className="text-xs text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
                  >
                    <Plus size={14} /> Añadir Sección
                  </button>
                </div>

                <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                  {sections.map((sec, idx) => (
                    <div
                      key={sec.id}
                      className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-2 text-xs"
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-400 w-5">{idx + 1}.</span>
                        <input
                          type="text"
                          value={sec.title}
                          onChange={(e) => updateSectionField(idx, 'title', e.target.value)}
                          placeholder="Título de la sección..."
                          className="flex-1 p-1.5 border border-slate-300 rounded bg-white focus:outline-none focus:border-blue-500 text-xs font-medium"
                        />
                        <button
                          onClick={() => removeSection(idx)}
                          className="text-slate-400 hover:text-red-500 p-1"
                          title="Eliminar sección"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>

                      <div className="pl-7">
                        <input
                          type="text"
                          value={sec.instructions}
                          onChange={(e) => updateSectionField(idx, 'instructions', e.target.value)}
                          placeholder="Instrucciones para redacción o asistencia IA en esta sección..."
                          className="w-full p-1.5 border border-slate-200 rounded bg-white text-slate-600 text-xs focus:outline-none focus:border-blue-400"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end pt-3 border-t border-slate-200">
                <button
                  onClick={handleSaveNativeTemplate}
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md text-xs font-semibold flex items-center gap-1.5 shadow-sm"
                >
                  {isSubmitting ? <Loader2 className="animate-spin" size={14} /> : <Check size={14} />}
                  <span>Guardar y Abrir en Editor</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
