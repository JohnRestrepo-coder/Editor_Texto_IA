import React from 'react';
import { Editor } from '@tiptap/react';
import {
  Bold,
  Italic,
  Underline as UnderlineIcon,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  Quote,
  Table as TableIcon,
  Undo2,
  Redo2,
  Minus
} from 'lucide-react';

interface EditorToolbarProps {
  editor: Editor | null;
}

export const EditorToolbar: React.FC<EditorToolbarProps> = ({ editor }) => {
  if (!editor) return null;

  const btnClass = (active: boolean) =>
    `p-2 rounded hover:bg-slate-200 transition-colors ${
      active ? 'bg-slate-200 text-blue-600 font-bold' : 'text-slate-700'
    }`;

  const insertTable = () => {
    editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run();
  };

  return (
    <div className="flex flex-wrap items-center gap-1 border-b border-slate-200 bg-slate-50 px-4 py-2 text-sm sticky top-0 z-10">
      <button
        type="button"
        onClick={() => editor.chain().focus().toggleBold().run()}
        disabled={!editor.can().chain().focus().toggleBold().run()}
        className={btnClass(editor.isActive('bold'))}
        title="Negrita (Ctrl+B)"
      >
        <Bold size={16} />
      </button>

      <button
        type="button"
        onClick={() => editor.chain().focus().toggleItalic().run()}
        disabled={!editor.can().chain().focus().toggleItalic().run()}
        className={btnClass(editor.isActive('italic'))}
        title="Cursiva (Ctrl+I)"
      >
        <Italic size={16} />
      </button>

      <button
        type="button"
        onClick={() => editor.chain().focus().toggleUnderline().run()}
        className={btnClass(editor.isActive('underline'))}
        title="Subrayado (Ctrl+U)"
      >
        <UnderlineIcon size={16} />
      </button>

      <div className="h-4 w-[1px] bg-slate-300 mx-1" />

      <button
        type="button"
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        className={btnClass(editor.isActive('heading', { level: 1 }))}
        title="Encabezado 1"
      >
        <Heading1 size={16} />
      </button>

      <button
        type="button"
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        className={btnClass(editor.isActive('heading', { level: 2 }))}
        title="Encabezado 2"
      >
        <Heading2 size={16} />
      </button>

      <button
        type="button"
        onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        className={btnClass(editor.isActive('heading', { level: 3 }))}
        title="Encabezado 3"
      >
        <Heading3 size={16} />
      </button>

      <div className="h-4 w-[1px] bg-slate-300 mx-1" />

      <button
        type="button"
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        className={btnClass(editor.isActive('bulletList'))}
        title="Lista de viñetas"
      >
        <List size={16} />
      </button>

      <button
        type="button"
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        className={btnClass(editor.isActive('orderedList'))}
        title="Lista numerada"
      >
        <ListOrdered size={16} />
      </button>

      <button
        type="button"
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        className={btnClass(editor.isActive('blockquote'))}
        title="Cita"
      >
        <Quote size={16} />
      </button>

      <button
        type="button"
        onClick={() => editor.chain().focus().setHorizontalRule().run()}
        className={btnClass(false)}
        title="Línea horizontal"
      >
        <Minus size={16} />
      </button>

      <div className="h-4 w-[1px] bg-slate-300 mx-1" />

      <button
        type="button"
        onClick={insertTable}
        className={btnClass(editor.isActive('table'))}
        title="Insertar tabla (3x3)"
      >
        <TableIcon size={16} />
      </button>

      <div className="h-4 w-[1px] bg-slate-300 mx-1" />

      <button
        type="button"
        onClick={() => editor.chain().focus().undo().run()}
        disabled={!editor.can().undo()}
        className="p-2 rounded hover:bg-slate-200 text-slate-700 disabled:opacity-40"
        title="Deshacer (Ctrl+Z)"
      >
        <Undo2 size={16} />
      </button>

      <button
        type="button"
        onClick={() => editor.chain().focus().redo().run()}
        disabled={!editor.can().redo()}
        className="p-2 rounded hover:bg-slate-200 text-slate-700 disabled:opacity-40"
        title="Rehacer (Ctrl+Y)"
      >
        <Redo2 size={16} />
      </button>
    </div>
  );
};
