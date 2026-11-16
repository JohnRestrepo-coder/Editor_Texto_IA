import React from 'react';
import type { DocumentListItem } from '../types/document';
import { FileText, Plus, Trash2, Clock } from 'lucide-react';

interface SidebarProps {
  documents: DocumentListItem[];
  currentDocId?: string;
  onSelectDoc: (id: string) => void;
  onCreateNew: () => void;
  onDeleteDoc: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  documents,
  currentDocId,
  onSelectDoc,
  onCreateNew,
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

      <div className="p-3">
        <button
          onClick={onCreateNew}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 px-4 rounded-md shadow transition-colors text-sm"
        >
          <Plus size={18} />
          <span>Nuevo Documento</span>
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
                  <span className="font-medium truncate">{doc.title}</span>
                  <span className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                    <Clock size={11} />
                    v{doc.version} · {new Date(doc.updated_at).toLocaleDateString()}
                  </span>
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
        AI Document Studio v0.1.0 · Monousuario
      </div>
    </aside>
  );
};
