export interface Section {
  id: string;
  title: string;
  position: number;
  required: boolean;
  instructions: string;
  generation_enabled: boolean;
  depends_on?: string[];
}

export interface Template {
  id: string;
  name: string;
  description?: string | null;
  source_type: 'native' | 'docx';
  source_file_id?: string | null;
  language: string;
  sections: Section[];
  style_profile?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface TemplateListItem {
  id: string;
  name: string;
  description?: string | null;
  source_type: 'native' | 'docx';
  sections_count: number;
  created_at: string;
  updated_at: string;
}

export interface TemplateCreatePayload {
  name: string;
  description?: string;
  source_type?: 'native' | 'docx';
  source_file_id?: string;
  language?: string;
  sections: Section[];
  style_profile?: Record<string, any>;
}

export interface DocxInspectionResult {
  template_id: string;
  filename: string;
  source_file_id: string;
  detected_sections: Section[];
  headings_count: number;
  paragraphs_count: number;
  tables_count: number;
  unsupported_elements: string[];
}
