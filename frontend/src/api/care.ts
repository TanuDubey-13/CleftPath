import { apiClient } from '../lib/apiClient';
import {
  ApiResponse,
  CareOverview,
  CareQueryParams,
  FeedingLog,
  FeedingLogCreateRequest,
  FeedingLogUpdateRequest,
  GrowthRecord,
  GrowthRecordCreateRequest,
  GrowthRecordUpdateRequest,
  NAMTapingLog,
  NAMTapingLogCreateRequest,
  NAMTapingLogUpdateRequest,
  PaginatedFeedingLogs,
  PaginatedGrowthRecords,
  PaginatedNAMLogs,
} from '../types';

const buildQueryString = (params?: CareQueryParams): string => {
  if (!params) return '';
  const search = new URLSearchParams();
  if (params.patient_id) search.set('patient_id', params.patient_id);
  if (params.start_date) search.set('start_date', params.start_date);
  if (params.end_date) search.set('end_date', params.end_date);
  if (params.page) search.set('page', params.page.toString());
  if (params.page_size) search.set('page_size', params.page_size.toString());
  const qs = search.toString();
  return qs ? `?${qs}` : '';
};

// ============================================================================
// Care Overview
// ============================================================================

export const fetchCareOverview = async (patientId?: string): Promise<CareOverview> => {
  const url = patientId ? `/care/overview?patient_id=${patientId}` : '/care/overview';
  const response = await apiClient.get<ApiResponse<CareOverview>>(url);
  return response.data.data;
};

// ============================================================================
// Feeding API
// ============================================================================

export const fetchFeedingLogs = async (params?: CareQueryParams): Promise<PaginatedFeedingLogs> => {
  const response = await apiClient.get<ApiResponse<PaginatedFeedingLogs>>(
    `/care/feeding${buildQueryString(params)}`
  );
  return response.data.data;
};

export const fetchFeedingLogDetail = async (logId: string): Promise<FeedingLog> => {
  const response = await apiClient.get<ApiResponse<FeedingLog>>(`/care/feeding/${logId}`);
  return response.data.data;
};

export const createFeedingLog = async (payload: FeedingLogCreateRequest): Promise<FeedingLog> => {
  const response = await apiClient.post<ApiResponse<FeedingLog>>('/care/feeding', payload);
  return response.data.data;
};

export const updateFeedingLog = async (
  logId: string,
  payload: FeedingLogUpdateRequest
): Promise<FeedingLog> => {
  const response = await apiClient.patch<ApiResponse<FeedingLog>>(`/care/feeding/${logId}`, payload);
  return response.data.data;
};

export const deleteFeedingLog = async (logId: string): Promise<void> => {
  await apiClient.delete(`/care/feeding/${logId}`);
};

// ============================================================================
// Growth API
// ============================================================================

export const fetchGrowthRecords = async (params?: CareQueryParams): Promise<PaginatedGrowthRecords> => {
  const response = await apiClient.get<ApiResponse<PaginatedGrowthRecords>>(
    `/care/growth${buildQueryString(params)}`
  );
  return response.data.data;
};

export const fetchGrowthRecordDetail = async (recordId: string): Promise<GrowthRecord> => {
  const response = await apiClient.get<ApiResponse<GrowthRecord>>(`/care/growth/${recordId}`);
  return response.data.data;
};

export const createGrowthRecord = async (payload: GrowthRecordCreateRequest): Promise<GrowthRecord> => {
  const response = await apiClient.post<ApiResponse<GrowthRecord>>('/care/growth', payload);
  return response.data.data;
};

export const updateGrowthRecord = async (
  recordId: string,
  payload: GrowthRecordUpdateRequest
): Promise<GrowthRecord> => {
  const response = await apiClient.patch<ApiResponse<GrowthRecord>>(`/care/growth/${recordId}`, payload);
  return response.data.data;
};

export const deleteGrowthRecord = async (recordId: string): Promise<void> => {
  await apiClient.delete(`/care/growth/${recordId}`);
};

// ============================================================================
// NAM / Taping API
// ============================================================================

export const fetchNAMLogs = async (params?: CareQueryParams): Promise<PaginatedNAMLogs> => {
  const response = await apiClient.get<ApiResponse<PaginatedNAMLogs>>(
    `/care/nam${buildQueryString(params)}`
  );
  return response.data.data;
};

export const fetchNAMLogDetail = async (logId: string): Promise<NAMTapingLog> => {
  const response = await apiClient.get<ApiResponse<NAMTapingLog>>(`/care/nam/${logId}`);
  return response.data.data;
};

export const createNAMLog = async (payload: NAMTapingLogCreateRequest): Promise<NAMTapingLog> => {
  const response = await apiClient.post<ApiResponse<NAMTapingLog>>('/care/nam', payload);
  return response.data.data;
};

export const updateNAMLog = async (
  logId: string,
  payload: NAMTapingLogUpdateRequest
): Promise<NAMTapingLog> => {
  const response = await apiClient.patch<ApiResponse<NAMTapingLog>>(`/care/nam/${logId}`, payload);
  return response.data.data;
};

export const deleteNAMLog = async (logId: string): Promise<void> => {
  await apiClient.delete(`/care/nam/${logId}`);
};
