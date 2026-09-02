export interface PathGuideCitation {
  article_id?: string | null;
  title: string;
  category: string;
  slug?: string | null;
  summary?: string | null;
}

export interface PathGuideMessage {
  id: string;
  thread_id: string;
  role: 'user' | 'assistant' | 'system' | string;
  content: string;
  citations: PathGuideCitation[];
  safety_flags: Record<string, any>;
  tokens_used: number;
  created_at: string;
}

export interface PathGuideMessageCreateRequest {
  content: string;
}

export interface PaginatedPathGuideMessages {
  items: PathGuideMessage[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PathGuideThread {
  id: string;
  user_id: string;
  patient_id?: string | null;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: PathGuideMessage | null;
}

export interface PathGuideThreadCreateRequest {
  patient_id?: string | null;
  title?: string;
  initial_message?: string;
}

export interface PathGuideThreadUpdateRequest {
  title: string;
}

export interface PaginatedPathGuideThreads {
  items: PathGuideThread[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PathGuideSuggestedPrompt {
  id: string;
  category: string;
  prompt: string;
  description: string;
}

export interface PathGuideSuggestedPromptsResponse {
  prompts: PathGuideSuggestedPrompt[];
}
