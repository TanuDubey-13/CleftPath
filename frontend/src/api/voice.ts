import { apiClient } from '../lib/apiClient';
import {
  ApiResponse,
  PaginatedVoiceExercises,
  PaginatedVoiceSessions,
  VoiceExercise,
  VoiceOverview,
  VoiceQueryParams,
  VoiceSession,
  VoiceSessionCreateRequest,
  VoiceSessionUpdateRequest,
} from '../types';

const buildQueryString = (params?: VoiceQueryParams): string => {
  if (!params) return '';
  const search = new URLSearchParams();
  if (params.patient_id) search.set('patient_id', params.patient_id);
  if (params.exercise_id) search.set('exercise_id', params.exercise_id);
  if (params.stage_id !== undefined && params.stage_id !== null) search.set('stage_id', params.stage_id.toString());
  if (params.difficulty) search.set('difficulty', params.difficulty);
  if (params.start_date) search.set('start_date', params.start_date);
  if (params.end_date) search.set('end_date', params.end_date);
  if (params.page) search.set('page', params.page.toString());
  if (params.page_size) search.set('page_size', params.page_size.toString());
  const qs = search.toString();
  return qs ? `?${qs}` : '';
};

// ============================================================================
// Overview
// ============================================================================

export const fetchVoiceOverview = async (patientId?: string): Promise<VoiceOverview> => {
  const url = patientId ? `/voice/overview?patient_id=${patientId}` : '/voice/overview';
  const response = await apiClient.get<ApiResponse<VoiceOverview>>(url);
  return response.data.data;
};

// ============================================================================
// Exercises
// ============================================================================

export const fetchVoiceExercises = async (params?: VoiceQueryParams): Promise<PaginatedVoiceExercises> => {
  const response = await apiClient.get<ApiResponse<PaginatedVoiceExercises>>(
    `/voice/exercises${buildQueryString(params)}`
  );
  return response.data.data;
};

export const fetchVoiceExerciseDetail = async (exerciseId: string): Promise<VoiceExercise> => {
  const response = await apiClient.get<ApiResponse<VoiceExercise>>(`/voice/exercises/${exerciseId}`);
  return response.data.data;
};

// ============================================================================
// Sessions
// ============================================================================

export const fetchVoiceSessions = async (params?: VoiceQueryParams): Promise<PaginatedVoiceSessions> => {
  const response = await apiClient.get<ApiResponse<PaginatedVoiceSessions>>(
    `/voice/sessions${buildQueryString(params)}`
  );
  return response.data.data;
};

export const fetchVoiceSessionDetail = async (sessionId: string): Promise<VoiceSession> => {
  const response = await apiClient.get<ApiResponse<VoiceSession>>(`/voice/sessions/${sessionId}`);
  return response.data.data;
};

export const createVoiceSession = async (payload: VoiceSessionCreateRequest): Promise<VoiceSession> => {
  const response = await apiClient.post<ApiResponse<VoiceSession>>('/voice/sessions', payload);
  return response.data.data;
};

export const updateVoiceSession = async (
  sessionId: string,
  payload: VoiceSessionUpdateRequest
): Promise<VoiceSession> => {
  const response = await apiClient.patch<ApiResponse<VoiceSession>>(`/voice/sessions/${sessionId}`, payload);
  return response.data.data;
};

export const deleteVoiceSession = async (sessionId: string): Promise<void> => {
  await apiClient.delete(`/voice/sessions/${sessionId}`);
};
