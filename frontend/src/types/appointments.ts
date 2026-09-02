export type AppointmentStatus =
  | 'scheduled'
  | 'confirmed'
  | 'completed'
  | 'cancelled'
  | 'no_show';

export interface CareTeamMemberSummary {
  id: string;
  specialist_name: string;
  specialty: string;
  clinic_or_hospital?: string | null;
  contact_phone?: string | null;
  contact_email?: string | null;
}

export interface Appointment {
  id: string;
  patient_id: string;
  care_team_member_id?: string | null;
  specialist_name: string;
  specialty: string;
  clinic_location?: string | null;
  scheduled_at: string;
  duration_minutes: number;
  prep_questions: string[];
  summary_notes?: string | null;
  status: AppointmentStatus;
  created_at: string;
  updated_at: string;
  care_team_member?: CareTeamMemberSummary | null;
}

export interface AppointmentCreateRequest {
  patient_id?: string | null;
  specialist_name: string;
  specialty: string;
  clinic_location?: string | null;
  scheduled_at: string;
  duration_minutes?: number;
  prep_questions?: string[];
  summary_notes?: string | null;
  care_team_member_id?: string | null;
}

export interface AppointmentUpdateRequest {
  specialist_name?: string;
  specialty?: string;
  clinic_location?: string | null;
  scheduled_at?: string;
  duration_minutes?: number;
  prep_questions?: string[];
  summary_notes?: string | null;
  status?: AppointmentStatus;
  care_team_member_id?: string | null;
}

export interface PaginatedAppointments {
  items: Appointment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  upcoming_count: number;
  past_count: number;
  next_appointment?: Appointment | null;
}

export interface AppointmentQueryParams {
  patient_id?: string;
  timeframe?: 'upcoming' | 'past' | 'all';
  status?: AppointmentStatus;
  page?: number;
  page_size?: number;
}
