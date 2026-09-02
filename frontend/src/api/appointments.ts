import { apiClient } from '../lib/apiClient';
import {
  ApiResponse,
  Appointment,
  AppointmentCreateRequest,
  AppointmentQueryParams,
  AppointmentUpdateRequest,
  CareTeamMemberSummary,
  PaginatedAppointments,
} from '../types';

export const fetchAppointments = async (
  params?: AppointmentQueryParams
): Promise<PaginatedAppointments> => {
  const queryParams = new URLSearchParams();
  if (params?.patient_id) queryParams.set('patient_id', params.patient_id);
  if (params?.timeframe) queryParams.set('timeframe', params.timeframe);
  if (params?.status) queryParams.set('status', params.status);
  if (params?.page) queryParams.set('page', params.page.toString());
  if (params?.page_size) queryParams.set('page_size', params.page_size.toString());

  const queryStr = queryParams.toString();
  const url = queryStr ? `/appointments?${queryStr}` : '/appointments';

  const response = await apiClient.get<ApiResponse<PaginatedAppointments>>(url);
  return response.data.data;
};

export const fetchAppointmentDetail = async (
  appointmentId: string
): Promise<Appointment> => {
  const response = await apiClient.get<ApiResponse<Appointment>>(
    `/appointments/${appointmentId}`
  );
  return response.data.data;
};

export const createAppointment = async (
  payload: AppointmentCreateRequest
): Promise<Appointment> => {
  const response = await apiClient.post<ApiResponse<Appointment>>(
    '/appointments',
    payload
  );
  return response.data.data;
};

export const updateAppointment = async (
  appointmentId: string,
  payload: AppointmentUpdateRequest
): Promise<Appointment> => {
  const response = await apiClient.patch<ApiResponse<Appointment>>(
    `/appointments/${appointmentId}`,
    payload
  );
  return response.data.data;
};

export const cancelAppointment = async (
  appointmentId: string
): Promise<Appointment> => {
  const response = await apiClient.post<ApiResponse<Appointment>>(
    `/appointments/${appointmentId}/cancel`
  );
  return response.data.data;
};

export const fetchCareTeamMembers = async (
  patientId?: string
): Promise<CareTeamMemberSummary[]> => {
  const url = patientId ? `/appointments/care-team?patient_id=${patientId}` : '/appointments/care-team';
  const response = await apiClient.get<ApiResponse<CareTeamMemberSummary[]>>(url);
  return response.data.data;
};
