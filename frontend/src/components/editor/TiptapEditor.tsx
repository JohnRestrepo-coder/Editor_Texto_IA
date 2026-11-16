import React, { useEffect } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import { Table } from '@tiptap/extension-table';
import { TableRow } from '@tiptap/extension-table-row';
import { TableCell } from '@tiptap/extension-table-cell';
import { TableHeader } from '@tiptap/extension-table-header';
import Link from '@tiptap/extension-link';
import { EditorToolbar } from './EditorToolbar';
import type { DocumentContent } from '../../types/document';

interface TiptapEditorProps {
  initialContent: DocumentContent;
  onChange: (content: DocumentContent) => void;
  documentId?: string;
}

export const TiptapEditor: React.FC<TiptapEditorProps> = ({
  initialContent,
  onChange,
  documentId,
}) => {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
      }),
      Underline,
      Table.configure({
        resizable: true,
      }),
      TableRow,
      TableHeader,
      TableCell,
      Link.configure({
        openOnClick: false,
      }),
    ],
    content: initialContent as any,
    onUpdate: ({ editor }) => {
      const json = editor.getJSON();
      onChange(json as unknown as DocumentContent);
    },
    editorProps: {
      attributes: {
        class:
          'prose max-w-none focus:outline-none min-h-[600px] px-12 py-10 font-sans text-slate-800 leading-relaxed',
      },
    },
  });

  // Actualizar contenido cuando cambia de documento
  useEffect(() => {
    if (editor && initialContent) {
      const currentJson = editor.getJSON();
      if (JSON.stringify(currentJson) !== JSON.stringify(initialContent)) {
        editor.commands.setContent(initialContent as any);
      }
    }
  }, [documentId, editor]);

  return (
    <div className="flex flex-col h-full bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
      <EditorToolbar editor={editor} />
      <div className="flex-1 overflow-y-auto bg-slate-100 p-6 flex justify-center">
        <div className="w-full max-w-4xl bg-white min-h-[850px] shadow-md border border-slate-200 rounded p-4">
          <EditorContent editor={editor} />
        </div>
      </div>
    </div>
  );
};
