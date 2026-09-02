export interface VoiceExercise {
  id: string;
  title: string;
  target_phonemes: string[];
  stage_id?: number | null;
  prompt_text: string;
  instructions: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced' | string;
  created_at: string;
}

export interface PaginatedVoiceExercises {
  items: VoiceExercise[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface VoiceSession {
  id: string;
  patient_id: string;
  exercise_id?: string | null;
  recorded_at: string;
  audio_s3_key: string;
  duration_seconds: number;
  repetition_count: number;
  dsp_features_json: Record<string, any>;
  parent_notes?: string | null;
  created_at: string;
  exercise?: VoiceExercise | null;
}

export interface VoiceSessionCreateRequest {
  patient_id?: string | null;
  exercise_id?: string | null;
  recorded_at?: string | null;
  duration_seconds: number;
  repetition_count?: number;
  parent_notes?: string | null;
  audio_s3_key?: string | null;
  dsp_features_json?: Record<string, any>;
}

export interface VoiceSessionUpdateRequest {
  duration_seconds?: number;
  repetition_count?: number;
  parent_notes?: string | null;
}

export interface PaginatedVoiceSessions {
  items: VoiceSession[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  total_practice_minutes: number;
  total_sessions_count: number;
}

export interface VoiceOverview {
  patient_id: string;
  total_sessions_count: number;
  total_practice_minutes: number;
  unique_exercises_practiced: number;
  last_session?: VoiceSession | null;
  practice_guidance_notes: string[];
}

export interface VoiceQueryParams {
  patient_id?: string;
  exercise_id?: string;
  stage_id?: number;
  difficulty?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}
