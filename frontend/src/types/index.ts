export * from './health';
export * from './auth';
export * from './journey';
export * from './health_library';
export * from './appointments';
export * from './care';

export interface Patient {
  id: string;
  display_name: string;
  date_of_birth: string;
  gender: string;
  cleft_type_summary: string;
  current_stage_id: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
  };
  timestamp?: string;
}
