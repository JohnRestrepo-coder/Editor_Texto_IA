import React from 'react';
import { Node, mergeAttributes, ReactNodeViewRenderer, NodeViewWrapper } from '@tiptap/react';
import type { NodeViewProps } from '@tiptap/react';
import { Sparkles, Trash2, ArrowRightCircle, Sliders } from 'lucide-react';

export const AiBlockComponent: React.FC<NodeViewProps> = ({
  node,
  updateAttributes,
  deleteNode,
}) => {
  const { id, sectionTitle, instructions, status, mode } = node.attrs;

  const handleSelectBlock = () => {
    window.dispatchEvent(
      new CustomEvent('ai-block-selected', {
        detail: {
          blockId: id,
          sectionTitle: sectionTitle || 'Sección con IA',
          instructions: instructions || '',
          mode: mode || 'draft',
        },
      })
    );
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'generating':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full animate-pulse border border-amber-300">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
            Generando con IA...
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            Propuesta lista
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium bg-red-100 text-red-800 px-2 py-0.5 rounded-full border border-red-300">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
            Error al generar
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full border border-indigo-200">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
            Pendiente de redacción
          </span>
        );
    }
  };

  return (
    <NodeViewWrapper className="ai-block-node-wrapper my-4">
      <div
        onClick={handleSelectBlock}
        className="group relative border-2 border-dashed border-indigo-300 hover:border-indigo-500 bg-gradient-to-r from-indigo-50/90 via-purple-50/60 to-indigo-50/90 rounded-xl p-4.5 transition-all duration-200 shadow-xs hover:shadow-md cursor-pointer select-none"
      >
        {/* Cabecera del Bloque */}
        <div className="flex items-center justify-between gap-3 mb-2.5">
          <div className="flex items-center gap-2 flex-1">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-xs">
              <Sparkles size={15} />
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 flex-1">
              <span className="text-[11px] tracking-wider uppercase font-bold text-indigo-600">
                Bloque de IA
              </span>
              <input
                type="text"
                value={sectionTitle || ''}
                onClick={(e) => e.stopPropagation()}
                onChange={(e) => updateAttributes({ sectionTitle: e.target.value })}
                placeholder="Nombre de la sección..."
                className="font-semibold text-slate-800 text-sm bg-white/90 border border-indigo-200 hover:border-indigo-400 focus:border-indigo-600 focus:outline-none rounded px-2.5 py-0.5 transition-colors max-w-xs"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            {getStatusBadge()}
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                deleteNode();
              }}
              title="Eliminar bloque de IA"
              className="text-slate-400 hover:text-red-500 hover:bg-red-50 p-1.5 rounded-md transition-colors"
            >
              <Trash2 size={15} />
            </button>
          </div>
        </div>

        {/* Cuerpo / Vista previa de instrucciones */}
        <div className="bg-white/80 border border-indigo-100 rounded-lg p-3 flex items-center justify-between gap-4">
          <div className="flex-1 text-xs">
            {instructions ? (
              <p className="text-slate-700 line-clamp-2">
                <strong className="text-indigo-900">Instrucción:</strong> {instructions}
              </p>
            ) : (
              <p className="text-slate-400 italic">
                Haz clic aquí o pulsa &ldquo;Configurar con IA&rdquo; para agregar fuentes y redactar el contenido.
              </p>
            )}
          </div>

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              handleSelectBlock();
            }}
            className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow-xs transition-colors shrink-0"
          >
            <Sliders size={13} />
            <span>Configurar y Generar</span>
            <ArrowRightCircle size={13} />
          </button>
        </div>
      </div>
    </NodeViewWrapper>
  );
};

export const AiBlock = Node.create({
  name: 'aiBlock',
  group: 'block',
  atom: true,
  selectable: true,
  draggable: true,

  addAttributes() {
    return {
      id: {
        default: null,
      },
      sectionTitle: {
        default: 'Nueva Sección',
      },
      instructions: {
        default: '',
      },
      mode: {
        default: 'draft',
      },
      status: {
        default: 'pending',
      },
      generatedText: {
        default: '',
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="ai-block"]',
        getAttrs: (element) => {
          if (typeof element === 'string') return {};
          const el = element as HTMLElement;
          return {
            id: el.getAttribute('data-id'),
            sectionTitle: el.getAttribute('data-section-title') || 'Nueva Sección',
            instructions: el.getAttribute('data-instructions') || '',
            mode: el.getAttribute('data-mode') || 'draft',
            status: el.getAttribute('data-status') || 'pending',
            generatedText: el.getAttribute('data-generated-text') || '',
          };
        },
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      mergeAttributes(HTMLAttributes, {
        'data-type': 'ai-block',
        'data-id': HTMLAttributes.id,
        'data-section-title': HTMLAttributes.sectionTitle,
        'data-instructions': HTMLAttributes.instructions,
        'data-mode': HTMLAttributes.mode,
        'data-status': HTMLAttributes.status,
        'data-generated-text': HTMLAttributes.generatedText,
      }),
    ];
  },

  addNodeView() {
    return ReactNodeViewRenderer(AiBlockComponent);
  },
});
