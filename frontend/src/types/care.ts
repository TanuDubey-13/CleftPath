export type FeedingBottleType =
  | 'dr_browns_specialty'
  | 'pigeon_cleft'
  | 'medela_specialneeds_haberman'
  | 'syringe_with_tubing'
  | 'supplemental_nursing'
  | 'cup_open'
  | 'standard_bottle'
  | 'other';

export type RefluxSeverity = 'none' | 'mild' | 'moderate' | 'severe';

export interface FeedingLog {
  id: string;
  patient_id: string;
  logged_at: string;
  bottle_type: FeedingBottleType;
  volume_ml: number;
  duration_minutes: number;
  burping_breaks: number;
  reflux_severity: RefluxSeverity;
  notes?: string | null;
  created_at: string;
}

export interface FeedingLogCreateRequest {
  patient_id?: string | null;
  logged_at?: string | null;
  bottle_type: FeedingBottleType;
  volume_ml: number;
  duration_minutes: number;
  burping_breaks?: number;
  reflux_severity?: RefluxSeverity;
  notes?: string | null;
}

export interface FeedingLogUpdateRequest {
  logged_at?: string | null;
  bottle_type?: FeedingBottleType;
  volume_ml?: number;
  duration_minutes?: number;
  burping_breaks?: number;
  reflux_severity?: RefluxSeverity;
  notes?: string | null;
}

export interface PaginatedFeedingLogs {
  items: FeedingLog[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  today_total_volume_ml: number;
  today_total_feeds: number;
}

export interface GrowthRecord {
  id: string;
  patient_id: string;
  recorded_at: string;
  weight_kg: number;
  height_cm?: number | null;
  head_circumference_cm?: number | null;
  weight_percentile?: number | null;
  height_percentile?: number | null;
  created_at: string;
}

export interface GrowthRecordCreateRequest {
  patient_id?: string | null;
  recorded_at: string;
  weight_kg: number;
  height_cm?: number | null;
  head_circumference_cm?: number | null;
  weight_percentile?: number | null;
  height_percentile?: number | null;
}

export interface GrowthRecordUpdateRequest {
  recorded_at?: string;
  weight_kg?: number;
  height_cm?: number | null;
  head_circumference_cm?: number | null;
  weight_percentile?: number | null;
  height_percentile?: number | null;
}

export interface PaginatedGrowthRecords {
  items: GrowthRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  latest_weight_kg?: number | null;
}

export interface NAMTapingLog {
  id: string;
  patient_id: string;
  logged_at: string;
  hours_worn: number;
  appliance_cleaned: boolean;
  tape_changed: boolean;
  skin_condition: string;
  notes?: string | null;
  created_at: string;
}

export interface NAMTapingLogCreateRequest {
  patient_id?: string | null;
  logged_at?: string | null;
  hours_worn: number;
  appliance_cleaned?: boolean;
  tape_changed?: boolean;
  skin_condition?: string;
  notes?: string | null;
}

export interface NAMTapingLogUpdateRequest {
  logged_at?: string | null;
  hours_worn?: number;
  appliance_cleaned?: boolean;
  tape_changed?: boolean;
  skin_condition?: string;
  notes?: string | null;
}

export interface PaginatedNAMLogs {
  items: NAMTapingLog[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  today_hours_worn: number;
}

export interface CareOverview {
  patient_id: string;
  today_feeding_volume_ml: number;
  today_feeding_count: number;
  last_feeding?: FeedingLog | null;
  latest_growth?: GrowthRecord | null;
  previous_growth?: GrowthRecord | null;
  latest_nam_log?: NAMTapingLog | null;
  today_nam_hours: number;
  guidance_notes: string[];
}

export interface CareQueryParams {
  patient_id?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}
