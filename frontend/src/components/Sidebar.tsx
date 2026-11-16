import React from 'react';
import type { DocumentListItem } from '../types/document';
import { FileText, Plus, Trash2, Clock, Layers } from 'lucide-react';

interface SidebarProps {
  documents: DocumentListItem[];
  currentDocId?: string;
  onSelectDoc: (id: string) => void;
  onCreateNew: () => void;
  onOpenTemplateModal: () => void;
  onDeleteDoc: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  documents,
  currentDocId,
  onSelectDoc,
  onCreateNew,
  onOpenTemplateModal,
  onDeleteDoc,
}) => {
  return (
    <aside className="w-72 bg-slate-900 text-slate-100 flex flex-col h-screen border-r border-slate-800">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2 font-semibold text-lg text-white">
          <FileText className="text-blue-400" size={22} />
          <span>Document Studio</span>
        </div>
      </div>

      <div className="p-3 space-y-2">
        <button
          onClick={onCreateNew}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium py-2 px-3 rounded-md shadow-xs transition-colors text-xs"
        >
          <Plus size={16} />
          <span>Editor Libre</span>
        </button>

        <button
          onClick={onOpenTemplateModal}
          className="w-full flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium py-2 px-3 rounded-md transition-colors text-xs"
        >
          <Layers size={16} className="text-blue-400" />
          <span>Usar Plantilla / DOCX</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-1 space-y-1">
        <div className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Mis Documentos ({documents.length})
        </div>

        {documents.length === 0 ? (
          <div className="p-4 text-center text-xs text-slate-400">
            No hay documentos aún. ¡Crea el primero!
          </div>
        ) : (
          documents.map((doc) => {
            const isSelected = doc.id === currentDocId;
            return (
              <div
                key={doc.id}
                onClick={() => onSelectDoc(doc.id)}
                className={`group flex items-center justify-between p-2.5 rounded-md cursor-pointer transition-colors text-sm ${
                  isSelected
                    ? 'bg-blue-900/50 text-white border-l-4 border-blue-500'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <div className="flex flex-col truncate pr-2">
                  <div className="flex items-center gap-1.5 truncate">
                    <span className="font-medium truncate">{doc.title}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                    <span className="flex items-center gap-1">
                      <Clock size={11} />
                      v{doc.version}
                    </span>
                    {doc.template_id && (
                      <span className="bg-slate-800 text-blue-300 px-1.5 py-0.2 rounded text-[10px]">
                        Plantilla
                      </span>
                    )}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`¿Eliminar "${doc.title}"?`)) {
                      onDeleteDoc(doc.id);
                    }
                  }}
                  className="opacity-0 group-hover:opacity-100 hover:text-red-400 p-1 text-slate-400 transition-opacity"
                  title="Eliminar"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            );
          })
        )}
      </div>

      <div className="p-3 border-t border-slate-800 text-xs text-slate-400 text-center">
        AI Document Studio v0.2.0 · Fase 2
      </div>
    </aside>
  );
};
