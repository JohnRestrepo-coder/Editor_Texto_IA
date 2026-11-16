import type { DocumentContent } from './document';

export type GenerationStatus =
  | 'queued'
  | 'processing'
  | 'completed'
  | 'failed'
  | 'accepted'
  | 'rejected';

export interface GenerationMetadata {
  provider: string;
  model: string;
  prompt_version: string;
  latency_ms: number;
  tokens_used?: number;
  error_message?: string;
}

export interface SectionGenerationPayload {
  document_id: string;
  section_id: string;
  section_title?: string;
  user_instructions?: string;
  context?: Record<string, unknown>;
  source_ids?: string[];
  expected_document_version?: number;
}

export interface GenerationResponse {
  generation_id: string;
  document_id: string;
  section_id: string;
  section_title: string;
  status: GenerationStatus;
  content: DocumentContent | null;
  original_section_content?: { content: unknown[] } | null;
  metadata_info: GenerationMetadata;
  created_at: string;
}

export interface FullGenerationPayload {
  instructions?: string;
  expected_document_version?: number;
}

export interface FullGenerationResponse {
  document_id: string;
  total_sections: number;
  generations: GenerationResponse[];
  status: string;
}
