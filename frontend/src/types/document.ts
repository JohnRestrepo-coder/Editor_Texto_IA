export interface Mark {
  type: 'bold' | 'italic' | 'underline' | 'strike' | 'link' | 'textStyle';
  attrs?: Record<string, any>;
}

export interface Node {
  type:
    | 'paragraph'
    | 'heading'
    | 'bulletList'
    | 'orderedList'
    | 'listItem'
    | 'blockquote'
    | 'horizontalRule'
    | 'table'
    | 'tableRow'
    | 'tableCell'
    | 'text'
    | 'hardBreak'
    | 'image';
  attrs?: Record<string, any>;
  content?: Node[];
  text?: string;
  marks?: Mark[];
}

export interface DocumentContent {
  type: 'doc';
  content: Node[];
}

export interface Document {
  id: string;
  title: string;
  content: DocumentContent;
  version: number;
  template_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentListItem {
  id: string;
  title: string;
  version: number;
  template_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentCreatePayload {
  title: string;
  content?: DocumentContent;
  template_id?: string;
}

export interface DocumentUpdatePayload {
  title?: string;
  content?: DocumentContent;
  expected_version: number;
}
