export type MilestoneStatus = 'upcoming' | 'in_progress' | 'completed' | 'skipped';

export interface MilestoneNote {
  id: string;
  milestone_id: string;
  user_id: string;
  note_text: string;
  photo_s3_key?: string | null;
  created_at: string;
  author_name?: string | null;
}

export interface JourneyMilestone {
  id: string;
  patient_id: string;
  stage_id: number;
  title: string;
  description: string;
  target_age_months?: number | null;
  status: MilestoneStatus;
  is_custom: boolean;
  target_date?: string | null;
  completed_at?: string | null;
  notes_count: number;
  notes: MilestoneNote[];
}

export interface JourneyStage {
  id: number;
  stage_number: number;
  title: string;
  age_range_label: string;
  description: string;
  color_hex: string;
  status: 'completed' | 'in_progress' | 'upcoming';
  milestones: JourneyMilestone[];
  total_milestones: number;
  completed_milestones: number;
  progress_percentage: number;
}

export interface JourneyPatientSummary {
  id: string;
  display_name: string;
  date_of_birth: string;
  gender: string;
  cleft_lip: string;
  cleft_palate: string;
  cleft_alveolus: string;
}

export interface JourneySummary {
  total_milestones: number;
  completed_milestones: number;
  in_progress_milestones: number;
  upcoming_milestones: number;
  overall_progress_percentage: number;
  current_stage_number?: number | null;
  current_stage_title?: string | null;
}

export interface JourneyOverview {
  patient: JourneyPatientSummary | null;
  stages: JourneyStage[];
  summary: JourneySummary;
}

export interface MilestoneUpdateRequest {
  status?: MilestoneStatus;
  target_date?: string | null;
  completed_at?: string | null;
}

export interface MilestoneNoteCreateRequest {
  note_text: string;
  photo_s3_key?: string | null;
}
